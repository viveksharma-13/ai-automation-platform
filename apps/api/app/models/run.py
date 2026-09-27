from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base
from app.types import JSONVariant


class WorkflowRun(Base):
    __tablename__ = "workflow_runs"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    workflow_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("workflows.id", ondelete="CASCADE"), index=True)
    workflow_version_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("workflow_versions.id"), index=True)
    status: Mapped[str] = mapped_column(String(32), default="pending", index=True)
    trigger_type: Mapped[str] = mapped_column(String(64), default="manual")
    input_payload: Mapped[dict] = mapped_column(JSONVariant, default=dict)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    celery_task_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    duration_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_by: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    workflow: Mapped["Workflow"] = relationship(back_populates="runs")
    version: Mapped["WorkflowVersion"] = relationship()
    steps: Mapped[list[WorkflowRunStep]] = relationship(
        back_populates="run", cascade="all, delete-orphan"
    )


class WorkflowRunStep(Base):
    __tablename__ = "workflow_run_steps"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    run_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("workflow_runs.id", ondelete="CASCADE"), index=True)
    node_key: Mapped[str] = mapped_column(String(64))
    node_type: Mapped[str] = mapped_column(String(64))
    status: Mapped[str] = mapped_column(String(32), default="pending")
    attempt: Mapped[int] = mapped_column(Integer, default=1)
    input_payload: Mapped[dict] = mapped_column(JSONVariant, default=dict)
    output_payload: Mapped[dict] = mapped_column(JSONVariant, default=dict)
    logs: Mapped[list] = mapped_column(JSONVariant, default=list)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    duration_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    run: Mapped[WorkflowRun] = relationship(back_populates="steps")
