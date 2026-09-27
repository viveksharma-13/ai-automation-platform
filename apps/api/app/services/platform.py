from __future__ import annotations

import json
import logging
import secrets
import uuid
from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.errors import ConflictError, ForbiddenError, NotFoundError, UnauthorizedError, ValidationAppError
from app.models.audit import AuditLog
from app.models.credential import WorkflowCredential
from app.models.run import WorkflowRun, WorkflowRunStep
from app.models.user import User
from app.models.workflow import Workflow, WorkflowNode, WorkflowVersion
from app.models.workspace import Workspace, WorkspaceMember
from app.security.auth import create_access_token, hash_password, verify_password
from app.security.crypto import decrypt_secret, encrypt_secret
from app.workflow.dsl import WorkflowGraph

logger = logging.getLogger(__name__)


def write_audit(
    db: Session,
    *,
    action: str,
    resource_type: str,
    resource_id: str | None = None,
    user_id: uuid.UUID | None = None,
    workspace_id: uuid.UUID | None = None,
    extra: dict | None = None,
) -> None:
    db.add(
        AuditLog(
            user_id=user_id,
            workspace_id=workspace_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            extra_data=extra or {},
        )
    )


def register_user(db: Session, email: str, password: str, name: str) -> tuple[User, str]:
    existing = db.scalar(select(User).where(func.lower(User.email) == email.lower()))
    if existing:
        raise ConflictError("Email already registered")
    user = User(email=email.lower(), name=name, password_hash=hash_password(password))
    db.add(user)
    db.flush()
    workspace = Workspace(name=f"{name}'s workspace", created_by=user.id)
    db.add(workspace)
    db.flush()
    db.add(WorkspaceMember(workspace_id=workspace.id, user_id=user.id, role="owner"))
    write_audit(db, action="user.register", resource_type="user", resource_id=str(user.id), user_id=user.id)
    db.commit()
    db.refresh(user)
    return user, create_access_token(str(user.id))


def authenticate_user(db: Session, email: str, password: str) -> tuple[User, str]:
    user = db.scalar(select(User).where(func.lower(User.email) == email.lower()))
    if user is None or not verify_password(password, user.password_hash):
        raise UnauthorizedError("Invalid email or password")
    return user, create_access_token(str(user.id))


def require_membership(db: Session, user: User, workspace_id: uuid.UUID) -> WorkspaceMember:
    member = db.scalar(
        select(WorkspaceMember).where(
            WorkspaceMember.workspace_id == workspace_id,
            WorkspaceMember.user_id == user.id,
        )
    )
    if member is None:
        raise ForbiddenError("Not a member of this workspace")
    return member


def list_workspaces(db: Session, user: User) -> list[tuple[Workspace, str]]:
    rows = db.execute(
        select(Workspace, WorkspaceMember.role)
        .join(WorkspaceMember, WorkspaceMember.workspace_id == Workspace.id)
        .where(WorkspaceMember.user_id == user.id)
        .order_by(Workspace.created_at.desc())
    ).all()
    return [(ws, role) for ws, role in rows]


def create_workspace(db: Session, user: User, name: str) -> Workspace:
    workspace = Workspace(name=name, created_by=user.id)
    db.add(workspace)
    db.flush()
    db.add(WorkspaceMember(workspace_id=workspace.id, user_id=user.id, role="owner"))
    write_audit(
        db,
        action="workspace.create",
        resource_type="workspace",
        resource_id=str(workspace.id),
        user_id=user.id,
        workspace_id=workspace.id,
    )
    db.commit()
    db.refresh(workspace)
    return workspace


def get_workspace(db: Session, user: User, workspace_id: uuid.UUID) -> tuple[Workspace, str]:
    member = require_membership(db, user, workspace_id)
    workspace = db.get(Workspace, workspace_id)
    if workspace is None:
        raise NotFoundError("Workspace not found")
    return workspace, member.role


def empty_graph() -> dict:
    return WorkflowGraph(nodes=[], edges=[]).model_dump()


def persist_nodes(db: Session, version: WorkflowVersion, graph: WorkflowGraph) -> None:
    version.nodes.clear()
    db.flush()
    for node in graph.nodes:
        db.add(
            WorkflowNode(
                workflow_version_id=version.id,
                node_key=node.id,
                type=node.type.value,
                name=node.name,
                config=node.config,
                input_mapping=node.input_mapping,
                output_mapping=node.output_mapping,
                position_x=node.position.x,
                position_y=node.position.y,
            )
        )


def _parse_graph(raw: dict | WorkflowGraph | None) -> WorkflowGraph:
    if raw is None:
        return WorkflowGraph()
    graph = raw if isinstance(raw, WorkflowGraph) else WorkflowGraph.model_validate(raw)
    graph.validate_graph()
    return graph


def create_workflow(
    db: Session,
    user: User,
    workspace_id: uuid.UUID,
    name: str,
    description: str | None,
    graph: WorkflowGraph | None,
    schedule_cron: str | None,
    schedule_enabled: bool,
) -> Workflow:
    require_membership(db, user, workspace_id)
    parsed = _parse_graph(graph)
    wf = Workflow(
        workspace_id=workspace_id,
        name=name,
        description=description,
        status="draft",
        webhook_token=secrets.token_urlsafe(24),
        schedule_cron=schedule_cron,
        schedule_enabled=schedule_enabled,
    )
    db.add(wf)
    db.flush()
    version = WorkflowVersion(
        workflow_id=wf.id,
        version_number=1,
        graph=parsed.model_dump(),
        created_by=user.id,
    )
    db.add(version)
    db.flush()
    persist_nodes(db, version, parsed)
    wf.current_version_id = version.id
    write_audit(
        db,
        action="workflow.create",
        resource_type="workflow",
        resource_id=str(wf.id),
        user_id=user.id,
        workspace_id=workspace_id,
    )
    db.commit()
    return get_workflow(db, user, wf.id)


def get_workflow(db: Session, user: User, workflow_id: uuid.UUID) -> Workflow:
    wf = db.scalar(
        select(Workflow)
        .options(selectinload(Workflow.current_version).selectinload(WorkflowVersion.nodes))
        .where(Workflow.id == workflow_id)
    )
    if wf is None:
        raise NotFoundError("Workflow not found")
    require_membership(db, user, wf.workspace_id)
    return wf


def list_workflows(db: Session, user: User, workspace_id: uuid.UUID | None) -> list[Workflow]:
    stmt = select(Workflow).options(selectinload(Workflow.current_version))
    if workspace_id:
        require_membership(db, user, workspace_id)
        stmt = stmt.where(Workflow.workspace_id == workspace_id)
    else:
        stmt = stmt.join(WorkspaceMember, WorkspaceMember.workspace_id == Workflow.workspace_id).where(
            WorkspaceMember.user_id == user.id
        )
    return list(db.scalars(stmt.order_by(Workflow.updated_at.desc())).unique().all())


def update_workflow(db: Session, user: User, workflow_id: uuid.UUID, **fields) -> Workflow:
    wf = get_workflow(db, user, workflow_id)
    graph = fields.pop("graph", None)
    for key, value in fields.items():
        if value is not None:
            setattr(wf, key, value)
    if graph is not None:
        parsed = _parse_graph(graph)
        version = wf.current_version
        if version is None or version.published_at is not None:
            next_number = (version.version_number + 1) if version else 1
            version = WorkflowVersion(
                workflow_id=wf.id,
                version_number=next_number,
                graph=parsed.model_dump(),
                created_by=user.id,
            )
            db.add(version)
            db.flush()
            wf.current_version_id = version.id
        else:
            version.graph = parsed.model_dump()
        persist_nodes(db, version, parsed)
    write_audit(
        db,
        action="workflow.update",
        resource_type="workflow",
        resource_id=str(wf.id),
        user_id=user.id,
        workspace_id=wf.workspace_id,
    )
    db.commit()
    return get_workflow(db, user, workflow_id)


def delete_workflow(db: Session, user: User, workflow_id: uuid.UUID) -> None:
    wf = get_workflow(db, user, workflow_id)
    db.delete(wf)
    write_audit(
        db,
        action="workflow.delete",
        resource_type="workflow",
        resource_id=str(workflow_id),
        user_id=user.id,
        workspace_id=wf.workspace_id,
    )
    db.commit()


def publish_workflow(db: Session, user: User, workflow_id: uuid.UUID) -> Workflow:
    wf = get_workflow(db, user, workflow_id)
    version = wf.current_version
    if version is None:
        raise ValidationAppError("Workflow has no version to publish")
    parsed = _parse_graph(version.graph)
    if not parsed.nodes:
        raise ValidationAppError("Cannot publish an empty workflow")
    if version.published_at is None:
        version.published_at = datetime.now(UTC)
    wf.status = "active"
    write_audit(
        db,
        action="workflow.publish",
        resource_type="workflow",
        resource_id=str(wf.id),
        user_id=user.id,
        workspace_id=wf.workspace_id,
        extra={"version_id": str(version.id), "version_number": version.version_number},
    )
    db.commit()
    return get_workflow(db, user, workflow_id)


def create_workflow_version(db: Session, user: User, workflow_id: uuid.UUID) -> Workflow:
    wf = get_workflow(db, user, workflow_id)
    current = wf.current_version
    graph = _parse_graph(current.graph if current else None)
    next_number = (current.version_number + 1) if current else 1
    version = WorkflowVersion(
        workflow_id=wf.id,
        version_number=next_number,
        graph=graph.model_dump(),
        created_by=user.id,
    )
    db.add(version)
    db.flush()
    persist_nodes(db, version, graph)
    wf.current_version_id = version.id
    wf.status = "draft"
    db.commit()
    return get_workflow(db, user, workflow_id)


def enqueue_run(
    db: Session,
    *,
    workflow: Workflow,
    version: WorkflowVersion,
    trigger_type: str,
    input_payload: dict,
    user_id: uuid.UUID | None,
) -> WorkflowRun:
    if version.published_at is None and trigger_type != "manual":
        raise ValidationAppError("Only published versions can be triggered automatically")
    run = WorkflowRun(
        workflow_id=workflow.id,
        workflow_version_id=version.id,
        status="pending",
        trigger_type=trigger_type,
        input_payload=input_payload,
        created_by=user_id,
    )
    db.add(run)
    db.commit()
    db.refresh(run)
    from app.tasks import execute_workflow_run

    async_result = execute_workflow_run.delay(str(run.id))
    run.celery_task_id = async_result.id
    db.commit()
    db.refresh(run)
    return run


def start_run_for_user(
    db: Session, user: User, workflow_id: uuid.UUID, input_payload: dict, version_id: uuid.UUID | None
) -> WorkflowRun:
    wf = get_workflow(db, user, workflow_id)
    if version_id:
        version = db.get(WorkflowVersion, version_id)
        if version is None or version.workflow_id != wf.id:
            raise NotFoundError("Workflow version not found")
    else:
        version = wf.current_version
    if version is None:
        raise ValidationAppError("Workflow has no version")
    return enqueue_run(
        db,
        workflow=wf,
        version=version,
        trigger_type="manual",
        input_payload=input_payload,
        user_id=user.id,
    )


def get_run(db: Session, user: User, run_id: uuid.UUID) -> WorkflowRun:
    run = db.scalar(
        select(WorkflowRun)
        .options(selectinload(WorkflowRun.steps))
        .where(WorkflowRun.id == run_id)
    )
    if run is None:
        raise NotFoundError("Run not found")
    get_workflow(db, user, run.workflow_id)
    return run


def list_runs(
    db: Session, user: User, workspace_id: uuid.UUID | None, workflow_id: uuid.UUID | None
) -> list[WorkflowRun]:
    stmt = (
        select(WorkflowRun)
        .join(Workflow, Workflow.id == WorkflowRun.workflow_id)
        .join(WorkspaceMember, WorkspaceMember.workspace_id == Workflow.workspace_id)
        .where(WorkspaceMember.user_id == user.id)
        .options(selectinload(WorkflowRun.steps))
        .order_by(WorkflowRun.created_at.desc())
        .limit(100)
    )
    if workspace_id:
        require_membership(db, user, workspace_id)
        stmt = stmt.where(Workflow.workspace_id == workspace_id)
    if workflow_id:
        stmt = stmt.where(WorkflowRun.workflow_id == workflow_id)
    return list(db.scalars(stmt).unique().all())


def dashboard_stats(db: Session, user: User) -> dict:
    wf_q = (
        select(Workflow)
        .join(WorkspaceMember, WorkspaceMember.workspace_id == Workflow.workspace_id)
        .where(WorkspaceMember.user_id == user.id)
    )
    workflows = list(db.scalars(wf_q).unique().all())
    wf_ids = [w.id for w in workflows]
    total = len(workflows)
    active = len([w for w in workflows if w.status == "active"])
    if not wf_ids:
        return {
            "total_workflows": 0,
            "active_workflows": 0,
            "recent_runs": 0,
            "successful_runs": 0,
            "failed_runs": 0,
        }
    runs = list(
        db.scalars(select(WorkflowRun).where(WorkflowRun.workflow_id.in_(wf_ids))).all()
    )
    return {
        "total_workflows": total,
        "active_workflows": active,
        "recent_runs": len(runs),
        "successful_runs": len([r for r in runs if r.status == "completed"]),
        "failed_runs": len([r for r in runs if r.status == "failed"]),
    }


def create_credential(
    db: Session, user: User, workspace_id: uuid.UUID, name: str, credential_type: str, payload: dict
) -> WorkflowCredential:
    require_membership(db, user, workspace_id)
    encrypted = encrypt_secret(json.dumps(payload))
    cred = WorkflowCredential(
        workspace_id=workspace_id,
        name=name,
        credential_type=credential_type,
        encrypted_payload=encrypted,
    )
    db.add(cred)
    write_audit(
        db,
        action="credential.create",
        resource_type="credential",
        resource_id=None,
        user_id=user.id,
        workspace_id=workspace_id,
    )
    db.commit()
    db.refresh(cred)
    return cred


def list_credentials(db: Session, user: User, workspace_id: uuid.UUID) -> list[WorkflowCredential]:
    require_membership(db, user, workspace_id)
    return list(
        db.scalars(
            select(WorkflowCredential)
            .where(WorkflowCredential.workspace_id == workspace_id)
            .order_by(WorkflowCredential.name)
        ).all()
    )


def load_workspace_credentials(db: Session, workspace_id: uuid.UUID) -> dict[str, dict]:
    creds = db.scalars(
        select(WorkflowCredential).where(WorkflowCredential.workspace_id == workspace_id)
    ).all()
    out: dict[str, dict] = {}
    for cred in creds:
        out[str(cred.id)] = json.loads(decrypt_secret(cred.encrypted_payload))
    return out


def get_workflow_by_webhook_token(db: Session, token: str) -> Workflow:
    wf = db.scalar(
        select(Workflow)
        .options(selectinload(Workflow.current_version))
        .where(Workflow.webhook_token == token)
    )
    if wf is None:
        raise NotFoundError("Unknown webhook")
    return wf
