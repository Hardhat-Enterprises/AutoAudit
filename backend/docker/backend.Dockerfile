FROM python:3.11-slim

WORKDIR /app

COPY ./ ./

WORKDIR /app/backend/backend

CMD ["python", "app.py"]