# AutoAudit Monorepo - Dev Branch

## Project Overview
The dev branch is the active development and integration branch where all team members collaborate and contribute new features. Code here undergoes continuous testing, linting, and security analysis to ensure quality before promotion.

## Repository Structure
The repo remains organized into top-level folders by team:

/backend-api

/security

/frontend

/engine

/.github/workflows (for CI/CD)

Full commit history and traceability from forks have been preserved.

## Branching Strategy
- dev is the main integration branch.
- Feature branches are created off dev for individual teams.
- Pull requests targeting dev must pass all checks before merging.
- All changes are integrated through Pull Requests (PRs), with branch protections and CI checks enforced.

## CI/CD Pipeline Overview
- Linting & Code Quality: Runs on every PR using a path filter.
- Security Scanning (CodeQL, Grype): Integrated to catch vulnerabilities early.
- Docker Builds: Images are built and tagged with environment branch names here and pushed but not deployed.
- No production deploys occur from this branch.

## Contribution Guidelines
- Work within your designated team folder, keeping code modular and isolated.
- Follow project code style guides (enforced via automated linting/CI).
- All PRs must target the correct integration branch and include a clear description and relevant issue/PR references.
- Tag your team and relevant reviewers for all non-trivial work.

## Contact & Support
For support or questions, please:
- Reach out to the DevOps lead for pipeline or environment questions.
- Open issues with appropriate tags for tracking.
