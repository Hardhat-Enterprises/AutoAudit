WORKDIR /app

COPY engine/ ./engine/
COPY rules/ ./rules/
COPY test-configs/ ./test-configs/

CMD ["python", "engine/main.py"]
