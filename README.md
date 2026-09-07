# AutoAudit Monorepo - Main/Deployment Branch

## Project Overview
AutoAudit is a M365 compliance automation platform built by several specialist teams. This monorepo centralizes all codebases—including backend services, APIs, compliance scanners, and frontends—enabling unified CI/CD, streamlined development, and rapid automated deployments to the cloud.

## Documentation

- [Getting Started](docs/GETTING_STARTED.md) - Set up your development environment
- [Contributing Guide](docs/CONTRIBUTING.md) - Find where to contribute based on your skills

## Repository Structure
The repo follows the established modular structure:  
- `/backend-api`  
- `/security`  
- `/frontend`  
- `/engine`  
- `/infrastructure`  
- `/tools`  
- `/docs`  
- `/.github/workflows`

Full commit history and traceability from team forks are preserved.

## Branching Strategy
- PRs are merged into staging only after review and approval from team leads on dev.
- No direct commits to staging are allowed to ensure controlled releases.
- Approved staging code is promoted to main for production deployment.

## CI/CD Pipeline Overview
- Runs CodeQL security analysis on changed code.
- Runs super-linter code quality checks.
- Performs Docker image builds tagged with the staging environment.
- Conducts Grype vulnerability scans on built images.
- Pushes Docker images to Docker Hub on successful builds.

Note: Integration/end-to-end test suites and GCP staging cluster deployments are not yet configured. Production promotion should be verified manually until these are in place.

## Contribution Guidelines  
- Only merges from `staging` occur into `main`, following stringent review and testing.  
- Emergency fixes require expedited team approval and follow strict policies.  
- All merges are subject to passing full CI/CD and security gating.

## Contact & Support  
For production deployment queries:  
- Contact the DevOps lead managing GCP integration.  
- Report critical issues with `main` branch deployments on GitHub with relevant tags.
