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

# Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Application code
COPY . .

EXPOSE 8000

CMD ["uvicorn", "frontend.ui:app", "--host", "0.0.0.0", "--port", "8000"]
