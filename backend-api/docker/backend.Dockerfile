FROM python:3.11-slim

WORKDIR /app

COPY backend-api/ ./backend-api

CMD ["python", "backend-api/app/main.py"]