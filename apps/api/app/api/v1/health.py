from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from redis import Redis
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.config import get_settings
from app.db import get_db

router = APIRouter(tags=["health"])


@router.get("/health")
def health():
    return {"status": "ok", "service": "api"}


@router.get("/health/db")
def health_db(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=503, detail={"status": "error", "database": "down", "message": str(exc)}) from exc
    return {"status": "ok", "database": "up"}


@router.get("/health/redis")
def health_redis():
    settings = get_settings()
    try:
        client = Redis.from_url(settings.redis_url, socket_connect_timeout=2)
        pong = client.ping()
        if not pong:
            raise HTTPException(status_code=503, detail={"status": "error", "redis": "down"})
    except HTTPException:
        raise
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=503, detail={"status": "error", "redis": "down", "message": str(exc)}) from exc
    return {"status": "ok", "redis": "up"}
