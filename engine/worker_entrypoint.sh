#!/bin/bash
set -e

echo "AutoAudit Worker Container"
echo "=========================="
echo "Starting Celery worker with prefork pool..."
echo ""

# Run Celery worker with prefork pool
# --pool=prefork: Multiple worker processes, each with isolated event loop
# --concurrency=4: 4 worker processes (adjust based on container resources)
# --loglevel=info: Standard logging level
#
# Note: We use prefork instead of gevent because the collectors use asyncio/httpx.
# Each prefork worker process has its own event loop, avoiding conflicts.
exec celery -A worker.celery_app worker --pool=prefork --concurrency=4 --loglevel=info
