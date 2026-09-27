from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db import get_db
from app.models.user import User
from app.schemas.workspace import WorkspaceCreate, WorkspaceResponse
from app.services import platform as svc

router = APIRouter(prefix="/workspaces", tags=["workspaces"])


@router.post("", response_model=WorkspaceResponse, status_code=201)
def create_workspace(
    body: WorkspaceCreate,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    ws = svc.create_workspace(db, user, body.name)
    return WorkspaceResponse.model_validate(ws).model_copy(update={"role": "owner"})


@router.get("", response_model=list[WorkspaceResponse])
def list_workspaces(
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    rows = svc.list_workspaces(db, user)
    return [
        WorkspaceResponse.model_validate(ws).model_copy(update={"role": role}) for ws, role in rows
    ]


@router.get("/{workspace_id}", response_model=WorkspaceResponse)
def get_workspace(
    workspace_id: UUID,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    ws, role = svc.get_workspace(db, user, workspace_id)
    return WorkspaceResponse.model_validate(ws).model_copy(update={"role": role})
