from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class WorkflowCredential(Base):
    __tablename__ = "workflow_credentials"
    __table_args__ = (UniqueConstraint("workspace_id", "name", name="uq_workspace_credential_name"),)

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    workspace_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("workspaces.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(200))
    credential_type: Mapped[str] = mapped_column(String(64))  # openai | http_header | api_key
    encrypted_payload: Mapped[str] = mapped_column(String(8000))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    workspace: Mapped["Workspace"] = relationship(back_populates="credentials")
