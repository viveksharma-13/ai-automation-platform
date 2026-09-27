from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from app.schemas.auth import ORMModel
from app.workflow.dsl import WorkflowGraph


class WorkflowCreate(BaseModel):
    workspace_id: uuid.UUID
    name: str = Field(min_length=1, max_length=200)
    description: str | None = None
    graph: WorkflowGraph | None = None
    schedule_cron: str | None = None
    schedule_enabled: bool = False


class WorkflowUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = None
    graph: WorkflowGraph | None = None
    schedule_cron: str | None = None
    schedule_enabled: bool | None = None
    status: str | None = None


class WorkflowNodeResponse(ORMModel):
    id: uuid.UUID
    node_key: str
    type: str
    name: str
    config: dict[str, Any]
    input_mapping: dict[str, Any]
    output_mapping: dict[str, Any]
    position_x: float
    position_y: float


class WorkflowVersionResponse(ORMModel):
    id: uuid.UUID
    workflow_id: uuid.UUID
    version_number: int
    graph: dict[str, Any]
    published_at: datetime | None
    created_by: uuid.UUID
    created_at: datetime


class WorkflowResponse(ORMModel):
    id: uuid.UUID
    workspace_id: uuid.UUID
    name: str
    description: str | None
    status: str
    webhook_token: str | None = None
    schedule_cron: str | None
    schedule_enabled: bool
    current_version_id: uuid.UUID | None
    created_at: datetime
    updated_at: datetime
    current_version: WorkflowVersionResponse | None = None


class PublishResponse(BaseModel):
    workflow: WorkflowResponse
    version: WorkflowVersionResponse


class RunCreate(BaseModel):
    input: dict[str, Any] = Field(default_factory=dict)
    version_id: uuid.UUID | None = None


class RunStepResponse(ORMModel):
    id: uuid.UUID
    node_key: str
    node_type: str
    status: str
    attempt: int
    input_payload: dict[str, Any]
    output_payload: dict[str, Any]
    logs: list[Any]
    error_message: str | None
    duration_ms: int | None
    started_at: datetime | None
    finished_at: datetime | None


class RunResponse(ORMModel):
    id: uuid.UUID
    workflow_id: uuid.UUID
    workflow_version_id: uuid.UUID
    status: str
    trigger_type: str
    input_payload: dict[str, Any]
    error_message: str | None
    duration_ms: int | None
    started_at: datetime | None
    finished_at: datetime | None
    created_at: datetime
    steps: list[RunStepResponse] = Field(default_factory=list)


class CredentialCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    credential_type: str = Field(min_length=1, max_length=64)
    payload: dict[str, Any]


class CredentialResponse(ORMModel):
    id: uuid.UUID
    workspace_id: uuid.UUID
    name: str
    credential_type: str
    created_at: datetime
    updated_at: datetime


class DashboardStats(BaseModel):
    total_workflows: int
    active_workflows: int
    recent_runs: int
    successful_runs: int
    failed_runs: int
