# AutoAudit Docker Builds and Container Management

## Overview

This document provides an in-depth explanation of the Docker build process, container orchestration, and best practices for managing Docker images within the AutoAudit project.

## Dockerfile Structure

The project uses a multi-stage Dockerfile optimised for minimal image size and security:

- **Builder Stage**: Installs build dependencies, compiles source code, and runs tests.
- **Runtime Stage**: Copies only necessary artifacts from the builder stage, sets non-root user permissions, and configures entrypoints.

Example snippet:

```dockerfile
FROM python:3.11-slim AS builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --user -r requirements.txt

COPY src/ ./src
RUN python -m compileall src/

FROM python:3.11-slim

WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY --from=builder /app/src ./src

ENV PATH=/root/.local/bin:$PATH
USER 1000:1000

ENTRYPOINT ["python", "src/main.py"]
```

## Image Optimisation

- Use slim base images to reduce the attack surface.
- Remove build dependencies after compilation.
- Leverage Docker layer caching for faster builds.
- Scan images with Trivy integrated into the CI pipeline to detect vulnerabilities.

## Docker Compose Usage

`docker-compose.yml` defines local development and integration testing environments with services:

- `autoaudit-api`: The main backend service.
- `autoaudit-db`: PostgreSQL database with persistent volume.
- `autoaudit-redis`: Redis cache for token and rate limiting.
- `autoaudit-frontend`: React-based frontend served via Nginx.

Example command to start local environment:

```bash
docker-compose up --build
```

## Secrets Management

- Use `.env` files excluded from version control for local secrets.
- In CI/CD, secrets are injected via GitHub Actions secrets and environment variables.
- Avoid hardcoding secrets in Dockerfiles or source code.

## Container Security Best Practices

- Run containers as non-root users.
- Use a read-only filesystem where possible.
- Limit container capabilities using Docker security options.
- Regularly update base images and dependencies.

## Troubleshooting

- Use `docker logs <container>` to inspect container output.
- Use `docker exec -it <container> /bin/bash` for interactive debugging.
- Monitor resource usage with `docker stats`.

---

_Last updated: 2025-09-11_
