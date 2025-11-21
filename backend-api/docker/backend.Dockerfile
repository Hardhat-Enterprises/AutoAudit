FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# System dependencies for OCR (pytesseract)
RUN apt-get update \
    && apt-get install -y --no-install-recommends tesseract-ocr libtesseract-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY pyproject.toml uv.lock ./
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir \
        fastapi>=0.116.1 \
        pydantic>=2.11.7 \
        pydantic-settings>=2.10.1 \
        python-dotenv>=1.1.1 \
        uvicorn>=0.35.0 \
        python-multipart>=0.0.9 \
        pypdf>=4.3.1 \
        pillow>=10.4.0 \
        pytesseract>=0.3.13

# Copy application code and default environment
COPY app ./app
COPY .env.example .env

EXPOSE 3000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "3000"]
