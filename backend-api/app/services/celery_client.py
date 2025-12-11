"""Celery client for queueing tasks from the backend API."""

from celery import Celery
from celery.result import AsyncResult

from app.core.config import get_settings

settings = get_settings()

# Create Celery app connected to the same broker as the worker
celery_app = Celery(
    "autoaudit",
    broker=settings.REDIS_URL,
)

# Task routing
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    task_default_queue="autoaudit",
)


def queue_scan(scan_id: int) -> AsyncResult:
    """Queue a scan task for execution by the worker.

    Args:
        scan_id: The scan ID to process

    Returns:
        Celery AsyncResult for tracking task status
    """
    return celery_app.send_task(
        "worker.tasks.run_scan",
        args=[scan_id],
        queue="autoaudit",
    )


def get_task_status(task_id: str) -> dict:
    """Get the status of a task.

    Args:
        task_id: The Celery task ID

    Returns:
        Dict with task status info
    """
    result = AsyncResult(task_id, app=celery_app)
    return {
        "task_id": task_id,
        "status": result.status,
        "ready": result.ready(),
        "successful": result.successful() if result.ready() else None,
        "result": result.result if result.ready() else None,
    }
