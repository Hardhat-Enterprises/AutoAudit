# AutoAudit Monorepo

## Project Overview
AutoAudit is a M365 compliance automation platform built by several specialist teams. This monorepo centralizes all codebases—including backend services, APIs, compliance scanners, and frontends—enabling unified CI/CD, streamlined development, and rapid automated deployments to the cloud.

## Repository Structure
The repo is organized into dedicated top-level folders for each team/service. This ensures clear code ownership, auditability, and minimizes merge conflicts.

# API and Backend Team
/backend-api

# Security Team
/security

# Frontend and User EXP
/frontend

# Engine Team
/engine 

# DevOps Team
/.github/workflows

Each folder was imported from individual repos, preserving full commit history and enabling future traceability.

## Branching Strategy
- main: Production-ready, stable releases only
- dev: Active integration and development from all teams
- staging: Pre-release, final QA before production
- feature/<team>-<desc>: Team-specific branches for new features or fixes

All changes are integrated through Pull Requests (PRs), with branch protections and CI checks enforced.

## Contribution Guidelines
- Work within your designated team folder, keeping code modular and isolated.
- Follow project code style guides (enforced via automated linting/CI).
- All PRs must target the correct integration branch and include a clear description and relevant issue/PR references.
- Tag your team and relevant reviewers for all non-trivial work.
- Major structural changes should be discussed with the DevOps lead before implementation.

## CI/CD Pipeline Overview
- Automated with GitHub Actions and Google Cloud Build
- On PR or code push, path filters selectively trigger builds & tests only for affected services.
- On successful checks, images are built and pushed to Google Artifact Registry.
- Deployments to GCP Kubernetes clusters are triggered for the appropriate environment (dev/staging/production).
- All secrets and environment-specific settings are managed via Google Secret Manager and encrypted variables.

## Contact & Support
For support or questions, please:
- Contact your DevOps team lead directly
- Open an issue in this repository (use proper tags for devops, security, api, etc.)
