#!/bin/bash
set -e

echo "Running database migrations..."
uv run alembic upgrade head

echo "Seeding default admin user..."
uv run python -m app.db.init_db

echo "Starting application..."
exec uv run uvicorn app.main:app --host 0.0.0.0 --port 8000
