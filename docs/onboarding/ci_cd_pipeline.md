# AutoAudit CI/CD Pipeline Usage and Deployment Guide

## Overview

This document outlines the design, usage, and maintenance of the AutoAudit CI/CD pipeline, which is implemented using GitHub Actions. It covers pipeline stages, environment configuration, deployment processes, rollback strategies, and troubleshooting.

## Pipeline Architecture

The pipeline is defined in `.github/workflows/ci_cd.yml` and consists of the following stages:

1. **Checkout Code**  
   Clones the repository and checks out the relevant branch, including any submodules.

2. **Dependency Installation**  
   Installs Python dependencies using `pipenv` and Node.js dependencies using `npm ci` for deterministic installs.

3. **Static Code Analysis**  
   Runs SonarQube scanner and linters (e.g., `flake8`, `eslint`) to enforce code quality and security standards.

4. **Unit and Integration Testing**  
   Executes automated test suites with coverage reporting. Minimum coverage threshold is 90%.

5. **Docker Build and Security Scan**  
   Builds Docker images using multi-stage builds. Scans images with Trivy for vulnerabilities, with zero tolerance for critical/high-severity vulnerabilities.

6. **Push Docker Images**  
   Pushes images to Docker Hub or Azure Container Registry with immutable tags based on commit SHA.

7. **Deploy to Kubernetes**  
   Applies Terraform templates and Kubernetes manifests to staging or production clusters with a blue-green deployment strategy.

8. **Post-Deployment Validation**  
   Runs smoke tests and health checks to verify deployment success.

9. **Notification**  
   Sends deployment status notifications to Slack channels.

## Environment Variables and Secrets

- `AZURE_CREDENTIALS`: Azure service principal JSON for authentication.
- `DOCKERHUB_USERNAME` and `DOCKERHUB_TOKEN`: Docker registry credentials.
- `KUBE_CONFIG_DATA`: Base64 encoded Kubernetes config for cluster access.
- `SLACK_WEBHOOK_URL`: Slack webhook URL for notifications.
- `CI_ENVIRONMENT`: Target environment (`staging` or `production`).

Secrets are stored securely in GitHub repository settings and injected only during pipeline execution.

## Deployment Process

- **Staging Deployment**: Triggered on pushes to `develop`. Deploys to `staging` namespace with resource quotas and monitoring enabled.
- **Production Deployment**: Triggered on merges to `main`. Deploys to `production` namespace using blue-green deployment to ensure zero downtime.

## Rollback Strategy

- Rollbacks are automated via Kubernetes deployment rollbacks triggered by failed health checks.
- Manual rollback can be triggered by redeploying the last known good image tag.
- All deployment events are logged with timestamps and audit trails.

## Running the Pipeline Locally

Developers can simulate pipeline stages locally using Docker Compose and the provided scripts (`scripts/ci_local.sh`) to debug and iterate faster.

## Troubleshooting

- Check GitHub Actions logs for detailed error messages.
- Verify Dockerfile syntax and base image availability if the build fails.
- Confirm the validity of Azure credentials and Kubernetes config for authentication errors.
- Review test reports and coverage summaries for test failures.

## Maintenance and Updates

- Pipeline workflows are version-controlled and reviewed via pull requests.
- Security scanning tools and dependencies are updated quarterly.
- New pipeline stages require ADR documentation and team approval.

---

_Last updated: 2025-09-11_
