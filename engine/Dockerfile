FROM python:3.11-slim

WORKDIR /app

# Install system dependencies (for gevent and psycopg2)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user early, before any COPYs
RUN adduser --disabled-password --gecos "" --uid 1000 appuser
RUN chown appuser:appuser /app

# Copy and install Python dependencies
COPY --chown=appuser:appuser pyproject.toml .
RUN pip install --no-cache-dir .

# Copy application code
COPY --chown=appuser:appuser worker/ ./worker/
COPY --chown=appuser:appuser collectors/ ./collectors/
COPY --chown=appuser:appuser policies/ ./policies/
COPY --chown=appuser:appuser opa_client.py ./

# Set Python path to include /app
ENV PYTHONPATH=/app

# Copy entrypoint script and fix line endings
COPY --chown=appuser:appuser worker_entrypoint.sh .
RUN sed -i 's/\r$//' worker_entrypoint.sh && chmod +x worker_entrypoint.sh

USER appuser

CMD ["./worker_entrypoint.sh"]
