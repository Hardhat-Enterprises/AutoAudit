FROM python:3.11-slim

WORKDIR /app

COPY engine/engine/ ./engine/
COPY engine/rules/ ./rules/
COPY engine/test-configs/ ./test-configs/

CMD ["python", "engine/main.py"]
