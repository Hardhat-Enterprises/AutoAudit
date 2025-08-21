FROM python:3.11-slim

WORKDIR /app

COPY backend/requirements.txt ./backend/
COPY backend/backend/app.py/ ./backend/

CMD ["python", "backend/app.py"]