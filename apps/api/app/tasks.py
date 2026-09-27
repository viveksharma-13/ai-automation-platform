from __future__ import annotations

import json
import logging
import uuid
from datetime import UTC, datetime

from croniter import croniter
from sqlalchemy.orm import Session

from app.celery_app import celery_app
from app.config import get_settings
from app.db import SessionLocal
from app.models.run import WorkflowRun, WorkflowRunStep
from app.models.workflow import Workflow, WorkflowVersion
from app.services.platform import enqueue_run, load_workspace_credentials
from app.workflow.context import ExecutionContext, NodeResult
from app.workflow.dsl import WorkflowGraph, WorkflowNodeDSL
from app.workflow.engine import WorkflowCancelled, execute_graph

logger = logging.getLogger(__name__)


def _persist_step_start(db: Session, run: WorkflowRun, node: WorkflowNodeDSL, attempt: int, payload: dict) -> WorkflowRunStep:
    step = WorkflowRunStep(
        run_id=run.id,
        node_key=node.id,
        node_type=node.type.value,
        status="running",
        attempt=attempt,
        input_payload=payload,
        started_at=datetime.now(UTC),
    )
    db.add(step)
    db.commit()
    db.refresh(step)
    return step


def _persist_step_finish(db: Session, step: WorkflowRunStep, result: NodeResult, duration_ms: int) -> None:
    step.status = result.status
    step.output_payload = result.output
    step.logs = result.logs
    step.error_message = result.error
    step.duration_ms = duration_ms
    step.finished_at = datetime.now(UTC)
    db.add(step)
    db.commit()


@celery_app.task(name="app.tasks.execute_workflow_run", bind=True, max_retries=1)
def execute_workflow_run(self, run_id: str) -> dict:
    db = SessionLocal()
    started = datetime.now(UTC)
    try:
        run = db.get(WorkflowRun, uuid.UUID(run_id))
        if run is None:
            logger.error("Run %s not found", run_id)
            return {"status": "missing"}
        if run.status == "cancelled":
            return {"status": "cancelled"}

        run.status = "running"
        run.started_at = started
        db.commit()

        version = db.get(WorkflowVersion, run.workflow_version_id)
        workflow = db.get(Workflow, run.workflow_id)
        if version is None or workflow is None:
            run.status = "failed"
            run.error_message = "Missing workflow version"
            run.finished_at = datetime.now(UTC)
            db.commit()
            return {"status": "failed"}

        graph = WorkflowGraph.model_validate(version.graph)
        settings = get_settings()
        credentials = load_workspace_credentials(db, workflow.workspace_id)
        ctx = ExecutionContext(
            run_id=str(run.id),
            workspace_id=str(workflow.workspace_id),
            graph=graph,
            trigger_input=run.input_payload or {},
            credentials=credentials,
            openai_api_key=settings.openai_api_key or None,
            openai_default_model=settings.openai_default_model,
        )

        open_steps: dict[tuple[str, int], WorkflowRunStep] = {}

        def is_cancelled() -> bool:
            db.refresh(run)
            return run.status == "cancelled"

        def on_start(node: WorkflowNodeDSL, payload: dict, attempt: int) -> None:
            step = _persist_step_start(db, run, node, attempt, payload)
            open_steps[(node.id, attempt)] = step

        def on_finish(node: WorkflowNodeDSL, result: NodeResult, attempt: int, duration_ms: int) -> None:
            step = open_steps.get((node.id, attempt))
            if step is None:
                step = _persist_step_start(db, run, node, attempt, {})
            _persist_step_finish(db, step, result, duration_ms)

        try:
            status, details = execute_graph(
                graph,
                ctx,
                is_cancelled=is_cancelled,
                on_node_start=on_start,
                on_node_finish=on_finish,
            )
        except WorkflowCancelled:
            run.status = "cancelled"
            run.finished_at = datetime.now(UTC)
            run.duration_ms = int((run.finished_at - started).total_seconds() * 1000)
            db.commit()
            return {"status": "cancelled"}

        run.status = status
        run.error_message = details.get("error")
        run.finished_at = datetime.now(UTC)
        run.duration_ms = int((run.finished_at - started).total_seconds() * 1000)
        db.commit()
        return {"status": status, "details": json.loads(json.dumps(details, default=str))}
    except Exception as exc:  # noqa: BLE001
        logger.exception("Run %s crashed", run_id)
        run = db.get(WorkflowRun, uuid.UUID(run_id))
        if run:
            run.status = "failed"
            run.error_message = str(exc)
            run.finished_at = datetime.now(UTC)
            db.commit()
        raise
    finally:
        db.close()


@celery_app.task(name="app.tasks.dispatch_scheduled_workflows")
def dispatch_scheduled_workflows() -> int:
    db = SessionLocal()
    dispatched = 0
    try:
        now = datetime.now(UTC)
        workflows = (
            db.query(Workflow)
            .filter(Workflow.schedule_enabled.is_(True), Workflow.status == "active")
            .all()
        )
        for wf in workflows:
            if not wf.schedule_cron or not wf.current_version_id:
                continue
            try:
                cron = croniter(wf.schedule_cron, now)
                prev = cron.get_prev(datetime)
            except Exception:  # noqa: BLE001
                logger.warning("Invalid cron on workflow %s: %s", wf.id, wf.schedule_cron)
                continue
            # fire if previous tick was within the last 70 seconds
            if (now - prev.replace(tzinfo=UTC)).total_seconds() > 70:
                continue
            version = db.get(WorkflowVersion, wf.current_version_id)
            if version is None or version.published_at is None:
                continue
            enqueue_run(
                db,
                workflow=wf,
                version=version,
                trigger_type="schedule",
                input_payload={"scheduled_at": now.isoformat()},
                user_id=None,
            )
            dispatched += 1
        return dispatched
    finally:
        db.close()
