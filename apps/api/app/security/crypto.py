from __future__ import annotations

from cryptography.fernet import Fernet, InvalidToken

from app.config import get_settings
from app.errors import AppError


def _fernet() -> Fernet:
    key = get_settings().credentials_encryption_key
    if not key:
        raise AppError(500, "CREDENTIALS_ENCRYPTION_KEY is not configured", "encryption_misconfigured")
    try:
        return Fernet(key.encode() if isinstance(key, str) else key)
    except ValueError as exc:
        raise AppError(500, "CREDENTIALS_ENCRYPTION_KEY is invalid", "encryption_misconfigured") from exc


def encrypt_secret(plaintext: str) -> str:
    return _fernet().encrypt(plaintext.encode("utf-8")).decode("utf-8")


def decrypt_secret(token: str) -> str:
    try:
        return _fernet().decrypt(token.encode("utf-8")).decode("utf-8")
    except InvalidToken as exc:
        raise AppError(500, "Failed to decrypt credential", "decrypt_failed") from exc
