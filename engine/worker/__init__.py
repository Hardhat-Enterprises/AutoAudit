"""AutoAudit Celery worker package."""

from worker.celery_app import celery_app

__all__ = ["celery_app"]
