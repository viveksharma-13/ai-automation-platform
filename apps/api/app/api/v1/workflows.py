from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db import get_db
from app.models.user import User
from app.schemas.workflow import (
    CredentialCreate,
    CredentialResponse,
    DashboardStats,
    PublishResponse,
    RunCreate,
    RunResponse,
    WorkflowCreate,
    WorkflowResponse,
    WorkflowUpdate,
    WorkflowVersionResponse,
)
from app.services import platform as svc

router = APIRouter(tags=["workflows"])


@router.get("/dashboard/stats", response_model=DashboardStats)
def stats(
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    return DashboardStats(**svc.dashboard_stats(db, user))


@router.post("/workflows", response_model=WorkflowResponse, status_code=201)
def create_workflow(
    body: WorkflowCreate,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    return svc.create_workflow(
        db,
        user,
        body.workspace_id,
        body.name,
        body.description,
        body.graph,
        body.schedule_cron,
        body.schedule_enabled,
    )


@router.get("/workflows", response_model=list[WorkflowResponse])
def list_workflows(
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
    workspace_id: UUID | None = None,
):
    return svc.list_workflows(db, user, workspace_id)


@router.get("/workflows/{workflow_id}", response_model=WorkflowResponse)
def get_workflow(
    workflow_id: UUID,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    return svc.get_workflow(db, user, workflow_id)


@router.patch("/workflows/{workflow_id}", response_model=WorkflowResponse)
def update_workflow(
    workflow_id: UUID,
    body: WorkflowUpdate,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    return svc.update_workflow(db, user, workflow_id, **body.model_dump(exclude_unset=True))


@router.delete("/workflows/{workflow_id}", status_code=204)
def delete_workflow(
    workflow_id: UUID,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    svc.delete_workflow(db, user, workflow_id)


@router.post("/workflows/{workflow_id}/publish", response_model=PublishResponse)
def publish_workflow(
    workflow_id: UUID,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    wf = svc.publish_workflow(db, user, workflow_id)
    return PublishResponse(
        workflow=WorkflowResponse.model_validate(wf),
        version=WorkflowVersionResponse.model_validate(wf.current_version),
    )


@router.post("/workflows/{workflow_id}/versions", response_model=WorkflowResponse, status_code=201)
def create_version(
    workflow_id: UUID,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    return svc.create_workflow_version(db, user, workflow_id)


@router.post("/workflows/{workflow_id}/run", response_model=RunResponse, status_code=202)
def run_workflow(
    workflow_id: UUID,
    body: RunCreate,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    return svc.start_run_for_user(db, user, workflow_id, body.input, body.version_id)


@router.get("/runs", response_model=list[RunResponse])
def list_runs(
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
    workspace_id: UUID | None = None,
    workflow_id: UUID | None = None,
):
    return svc.list_runs(db, user, workspace_id, workflow_id)


@router.get("/runs/{run_id}", response_model=RunResponse)
def get_run(
    run_id: UUID,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    return svc.get_run(db, user, run_id)


@router.post("/workspaces/{workspace_id}/credentials", response_model=CredentialResponse, status_code=201)
def create_credential(
    workspace_id: UUID,
    body: CredentialCreate,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    return svc.create_credential(db, user, workspace_id, body.name, body.credential_type, body.payload)


@router.get("/workspaces/{workspace_id}/credentials", response_model=list[CredentialResponse])
def list_credentials(
    workspace_id: UUID,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    return svc.list_credentials(db, user, workspace_id)
