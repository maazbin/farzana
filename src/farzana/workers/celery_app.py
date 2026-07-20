"""Celery application — jobs that must not block the HTTP request path."""

from celery import Celery

from farzana.core.config import get_settings

settings = get_settings()

celery_app = Celery(
    "farzana",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=["farzana.workers.tasks"],
)

celery_app.conf.update(
    task_always_eager=settings.celery_task_always_eager,
    task_eager_propagates=True,
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    broker_connection_retry_on_startup=True,
)
