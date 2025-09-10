FROM python:3.11-slim

WORKDIR /app

COPY ./ ./

WORKDIR /app/backend

CMD ["python", "backend/main.py"]