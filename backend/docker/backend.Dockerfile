FROM python:3.11-slim

WORKDIR /app

COPY backend/backend/ /backend/

CMD ["python", "app.py"]