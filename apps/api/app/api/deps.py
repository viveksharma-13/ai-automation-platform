from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.db import get_db
from app.errors import UnauthorizedError
from app.models.user import User
from app.security.auth import decode_access_token

bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    creds: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    db: Annotated[Session, Depends(get_db)],
) -> User:
    if creds is None or creds.scheme.lower() != "bearer":
        raise UnauthorizedError()
    user_id = decode_access_token(creds.credentials)
    try:
        uid = uuid.UUID(user_id)
    except ValueError as exc:
        raise UnauthorizedError("Invalid token subject") from exc
    user = db.get(User, uid)
    if user is None:
        raise UnauthorizedError("User not found")
    return user
