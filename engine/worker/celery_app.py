"""Celery application configuration for AutoAudit worker."""

from celery import Celery

from worker.config import settings

# Create Celery app
celery_app = Celery(
    "autoaudit",
    broker=settings.REDIS_URL,
    # No result backend - results are written directly to PostgreSQL
)

# Configure Celery
celery_app.conf.update(
    # Serialization
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    # Timezone
    timezone="UTC",
    enable_utc=True,
    # Task tracking
    task_track_started=True,
    # Task routing
    task_default_queue="autoaudit",
    # Retry settings
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    # Concurrency (for gevent pool)
    worker_concurrency=10,
)

# Auto-discover tasks from the worker.tasks module
celery_app.autodiscover_tasks(["worker"])
