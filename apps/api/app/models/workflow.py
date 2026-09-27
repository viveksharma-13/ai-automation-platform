from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base
from app.types import JSONVariant


class Workflow(Base):
    __tablename__ = "workflows"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    workspace_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("workspaces.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(200))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="draft")  # draft | active | archived
    webhook_token: Mapped[str | None] = mapped_column(String(64), unique=True, nullable=True, index=True)
    schedule_cron: Mapped[str | None] = mapped_column(String(128), nullable=True)
    schedule_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    current_version_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("workflow_versions.id", use_alter=True, name="fk_workflows_current_version"),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    workspace: Mapped["Workspace"] = relationship(back_populates="workflows")
    versions: Mapped[list[WorkflowVersion]] = relationship(
        back_populates="workflow",
        foreign_keys="WorkflowVersion.workflow_id",
        cascade="all, delete-orphan",
    )
    current_version: Mapped[WorkflowVersion | None] = relationship(
        foreign_keys=[current_version_id], post_update=True
    )
    runs: Mapped[list["WorkflowRun"]] = relationship(back_populates="workflow")


class WorkflowVersion(Base):
    __tablename__ = "workflow_versions"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    workflow_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("workflows.id", ondelete="CASCADE"), index=True)
    version_number: Mapped[int] = mapped_column(Integer)
    graph: Mapped[dict] = mapped_column(JSONVariant, default=dict)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_by: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    workflow: Mapped[Workflow] = relationship(back_populates="versions", foreign_keys=[workflow_id])
    nodes: Mapped[list[WorkflowNode]] = relationship(
        back_populates="version", cascade="all, delete-orphan"
    )


class WorkflowNode(Base):
    __tablename__ = "workflow_nodes"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    workflow_version_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("workflow_versions.id", ondelete="CASCADE"), index=True
    )
    node_key: Mapped[str] = mapped_column(String(64))
    type: Mapped[str] = mapped_column(String(64))
    name: Mapped[str] = mapped_column(String(200))
    config: Mapped[dict] = mapped_column(JSONVariant, default=dict)
    input_mapping: Mapped[dict] = mapped_column(JSONVariant, default=dict)
    output_mapping: Mapped[dict] = mapped_column(JSONVariant, default=dict)
    position_x: Mapped[float] = mapped_column(default=0)
    position_y: Mapped[float] = mapped_column(default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    version: Mapped[WorkflowVersion] = relationship(back_populates="nodes")
