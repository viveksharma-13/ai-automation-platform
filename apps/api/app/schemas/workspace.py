from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.auth import ORMModel


class WorkspaceCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)


class WorkspaceResponse(ORMModel):
    id: uuid.UUID
    name: str
    created_by: uuid.UUID
    created_at: datetime
    updated_at: datetime
    role: str | None = None
