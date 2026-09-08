# Backend API Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies (incl. Tesseract for evidence OCR)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    tesseract-ocr \
    libtesseract-dev \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user early, before any COPYs
RUN adduser --disabled-password --gecos "" --uid 1000 appuser
RUN chown appuser:appuser /app

# Install uv
RUN pip install uv

# Copy dependency files and install dependencies
COPY --chown=appuser:appuser backend-api/pyproject.toml backend-api/uv.lock ./
RUN uv sync --frozen --no-dev --extra evidence \
    && chown -R appuser:appuser /app/.venv

# Copy application code
COPY --chown=appuser:appuser backend-api/app ./app
COPY --chown=appuser:appuser backend-api/alembic ./alembic
COPY --chown=appuser:appuser backend-api/alembic.ini backend-api/entrypoint.sh ./

# Copy evidence scanner assets/logic
COPY --chown=appuser:appuser security ./security

# Make entrypoint executable
RUN chmod +x entrypoint.sh

# Expose port
EXPOSE 8000

USER appuser

# Run migrations and start the application
ENTRYPOINT ["./entrypoint.sh"]
