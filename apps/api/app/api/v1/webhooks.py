from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.db import get_db
from app.errors import ValidationAppError
from app.schemas.workflow import RunResponse
from app.services import platform as svc

router = APIRouter(tags=["webhooks"])


@router.post("/webhooks/{token}", response_model=RunResponse, status_code=202)
async def inbound_webhook(token: str, request: Request, db: Annotated[Session, Depends(get_db)]):
    wf = svc.get_workflow_by_webhook_token(db, token)
    version = wf.current_version
    if version is None or version.published_at is None:
        raise ValidationAppError("Webhook is not active until the workflow is published")
    payload: Any
    try:
        payload = await request.json()
    except Exception:
        payload = {}
    if not isinstance(payload, dict):
        payload = {"body": payload}
    run = svc.enqueue_run(
        db,
        workflow=wf,
        version=version,
        trigger_type="webhook",
        input_payload=payload,
        user_id=None,
    )
    return run
