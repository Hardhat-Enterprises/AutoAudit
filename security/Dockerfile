# Evidence API Dockerfile
# Builds a lightweight FastAPI service that powers the Evidence Scanner UI.

FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# System packages needed for OCR (Tesseract). Keep the image small by avoiding
# optional PDF converters (LibreOffice) — the app falls back gracefully.
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
      tesseract-ocr \
      libtesseract-dev && \
    rm -rf /var/lib/apt/lists/*

# Create non-root user early, before any COPYs
RUN adduser --disabled-password --gecos "" --uid 1000 appuser
RUN chown appuser:appuser /app

# Python dependencies
COPY --chown=appuser:appuser requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Application code
COPY --chown=appuser:appuser . .

EXPOSE 8000

USER appuser

CMD ["uvicorn", "evidence_ui.app:app", "--host", "0.0.0.0", "--port", "8000"]
