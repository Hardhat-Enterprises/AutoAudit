# Use a lightweight Python base image
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Copy only necessary files
COPY engine/ ./engine/
COPY rules/ ./rules/
COPY test-configs/ ./test-configs/

# Set the default command to run the rule engine
CMD ["python", "engine/main.py", "test-configs/compliant.json", "rules/CIS_1.1.2.json"]
