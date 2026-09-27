from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db import get_db
from app.models.user import User
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse, UserResponse
from app.services import platform as svc

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse, status_code=201)
def register(body: RegisterRequest, db: Annotated[Session, Depends(get_db)]):
    _, token = svc.register_user(db, body.email, body.password, body.name)
    return TokenResponse(access_token=token)


@router.post("/login", response_model=TokenResponse)
def login(body: LoginRequest, db: Annotated[Session, Depends(get_db)]):
    _, token = svc.authenticate_user(db, body.email, body.password)
    return TokenResponse(access_token=token)


@router.get("/me", response_model=UserResponse)
def me(user: Annotated[User, Depends(get_current_user)]):
    return user
