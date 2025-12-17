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
- `/.github/workflows`

Full commit history and traceability from team forks are preserved.

## Branching Strategy  
- Only trusted, verified releases from `staging` are merged into `main`.
- Direct commits are prohibited via branch protection rules.
- Changes in `main` trigger the production deployment workflows.

## CI/CD Pipeline Overview  
- Code scanning (CodeQL, Grype) and security validations run on every push or PR.
- Docker images are built and tagged for the `prod` environment here.
- **Production deployments to Google Cloud Platform (GCP) will be triggered from this branch once configured.**
- Currently, GCP deployment automation is being set up;  
  once complete, a GCP Cloud Build trigger will automatically build and deploy the `main` branch code and push images into the GCP Artifact Registry.

## Docker Builds  
- Production Docker images from the `main` branch are tagged appropriately and pushed to:  
  - [Docker Hub - AutoAudit Services](https://hub.docker.com/u/autoauditservices)  
  - GCP Artifact Registry (once integration is complete)  
- Individual service repos like Engine, Backend-API, Frontend, and Security have mirrored deployment artifacts.

## Contribution Guidelines  
- Only merges from `staging` occur into `main`, following stringent review and testing.  
- Emergency fixes require expedited team approval and follow strict policies.  
- All merges are subject to passing full CI/CD and security gating.

## Contact & Support  
For production deployment queries:  
- Contact the DevOps lead managing GCP integration.  
- Report critical issues with `main` branch deployments on GitHub with relevant tags.
