FROM python:3.11-slim
WORKDIR /app

COPY engine/ ./engine/
COPY rules/ ./rules/
COPY test-configs/ ./test-configs/

CMD ["python", "engine/main.py"]
