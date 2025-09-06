FROM python:3.11-slim

WORKDIR /app

COPY engine/ ./engine/

CMD ["python", "engine/main.py"]
