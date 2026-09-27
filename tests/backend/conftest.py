"""Pytest configuration — env must be set before the API package is imported."""

from __future__ import annotations

import os
import sys
from pathlib import Path

from cryptography.fernet import Fernet

ROOT = Path(__file__).resolve().parents[2]
API_ROOT = ROOT / "apps" / "api"
sys.path.insert(0, str(API_ROOT))

os.environ.setdefault("APP_ENV", "test")
os.environ["DATABASE_URL"] = "sqlite+pysqlite:///" + str(ROOT / "tests" / "backend" / "test.db").replace("\\", "/")
os.environ["JWT_SECRET"] = "test-jwt-secret-test-jwt-secret-test"
os.environ["CREDENTIALS_ENCRYPTION_KEY"] = Fernet.generate_key().decode()
os.environ["CELERY_TASK_ALWAYS_EAGER"] = "true"
os.environ["CELERY_BROKER_URL"] = "memory://"
os.environ["CELERY_RESULT_BACKEND"] = "cache+memory://"
os.environ["REDIS_URL"] = "redis://localhost:6379/0"
os.environ["WEB_ORIGIN"] = "http://localhost:3000"

from app.config import get_settings  # noqa: E402

get_settings.cache_clear()
