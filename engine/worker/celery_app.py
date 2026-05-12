"""Celery application configuration for AutoAudit worker."""

from celery import Celery

from worker.config import settings

# Queue names. Workers run with --queues=<one of these> so each Deployment
# only consumes its own queue and can be scaled independently. Adding a new
# queue here also requires a new entry in helm/autoaudit/values.yaml under
# `worker.queues:` so Helm renders a Deployment for it.
QUEUE_DEFAULT = "default"
QUEUE_CONTROLS_GRAPH = "controls.graph"
QUEUE_CONTROLS_POWERSHELL = "controls.powershell"

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
    # The orchestrator and any un-routed task lands here.
    task_default_queue=QUEUE_DEFAULT,
    # Retry settings
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    # Concurrency (overridden per-Deployment via the worker --concurrency CLI flag).
    worker_concurrency=10,
)

# Auto-discover tasks from the worker.tasks module
celery_app.autodiscover_tasks(["worker"])
