from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base
from app.types import JSONVariant


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id"), nullable=True, index=True)
    workspace_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("workspaces.id"), nullable=True, index=True
    )
    action: Mapped[str] = mapped_column(String(128))
    resource_type: Mapped[str] = mapped_column(String(64))
    resource_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    extra_data: Mapped[dict] = mapped_column(JSONVariant, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
