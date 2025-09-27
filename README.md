# AutoAudit Monorepo - Staging Branch

## Staging Environment Overview
The staging branch serves as the pre-production environment where integrated and tested code from dev is thoroughly validated. This branch is used for final QA, security checks, and end-to-end testing before production deployment.

## Staging Branch Structure
The repo maintains the same top-level folder structure by team:

- /backend-api
- /security
- /frontend
- /engine
- /.github/workflows (for CI/CD)

Commit history and code provenance are preserved from original forks and merges.

## Branching Strategu
- PRs are merged into staging only after review and approval from team leads on dev.
- No direct commits to staging are allowed to ensure controlled releases.
- Approved staging code is promoted to main for production deployment.

## CI/CD Pipeline Overview
- Runs full test suites including integration and end-to-end tests.
- Performs Docker image builds tagged with the staging environment.
- Conducts security scans (CodeQL, Grype) on built images.
- Automates deployment to GCP staging clusters for real-world validation.

Production deployment is triggered only after successful staging deployments.

## Contribution Guidelines
- Changes come only via PR merges from dev; no direct pushes allowed.
- Follow strict code review and quality assurance protocols.
- All PRs must include thorough testing and reference related issues.
- Tag relevant team leads and reviewers for approval.

## Docker Builds
Docker images built here are pushed with the staging tag to Docker Hub and GCP Artifact Registry.
- Teams can inspect and test staging images before promotion.
- Docker Hub: https://hub.docker.com/u/autoauditservices
- Engine Repo: https://hub.docker.com/r/autoauditservices/engine
- Backend-API Repo: https://hub.docker.com/r/autoauditservices/backend-api
- Frontend Repo: https://hub.docker.com/r/autoauditservices/frontend (unconfigged)
- Security Repo: https://hub.docker.com/r/autoauditservices/security (unconfigged)

## Contact & Support
For support or questions, please:
- Contact your DevOps or QA lead.
- Open issues in this repository with appropriate environment tags.
