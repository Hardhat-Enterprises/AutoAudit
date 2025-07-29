FROM python:3.11-slim
WORKDIR /app
COPY engine/ ./engine/
COPY rules/ ./rules/
COPY test-configs/ ./test-configs/
CMD ["python", "engine/main.py", "test-configs/compliant.json", "rules/CIS_1.1.2.json"]
