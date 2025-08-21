FROM python:3.11-slim

WORKDIR /app

COPY backend/requirements.txt ./backend/
COPY backend/backend/ ./backend/

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "backend/app.py"]