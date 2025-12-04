# Backend API Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies (incl. Tesseract for evidence OCR)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    tesseract-ocr \
    libtesseract-dev \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install uv

# Copy dependency files
COPY backend-api/pyproject.toml backend-api/uv.lock ./

# Install dependencies
RUN uv sync --frozen --no-dev

# Security (evidence) dependencies into the uv venv
COPY security/requirements.txt ./security/requirements.txt
RUN uv pip install --python .venv/bin/python -r security/requirements.txt

# Copy application code
COPY backend-api/app ./app
COPY backend-api/alembic ./alembic
COPY backend-api/alembic.ini ./
COPY backend-api/entrypoint.sh ./

# Copy evidence scanner assets/logic
COPY security ./security

# Make entrypoint executable
RUN chmod +x entrypoint.sh

# Expose port
EXPOSE 8000

# Run migrations and start the application
ENTRYPOINT ["./entrypoint.sh"]
