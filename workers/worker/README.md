"""Celery worker entrypoint.

The worker reuses the API package (models, engine, tasks) via PYTHONPATH.
Run from apps/api:

    celery -A app.celery_app:celery_app worker --loglevel=info
"""
