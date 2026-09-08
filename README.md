# AutoAudit Monorepo - Main/Deployment Branch

## Project Overview
AutoAudit is a M365 compliance automation platform built by several specialist teams. This monorepo centralizes all codebases—including backend services, APIs, compliance scanners, and frontends—so one set of CI gates covers the whole system. It does **not** deploy: there is no deployment pipeline, no target environment and no registry push.

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
- **Nothing in this repository pushes to a registry.** The three pull-request preview
  workflows that pushed mutable `pr-<number>` tags to GHCR have been removed; the deploy
  job among them could never finish, because `docker-compose.yml` has required
  `POSTGRES_PASSWORD` since `f7981302` and the workflow set it nowhere. The only other
  image build, in `ci.grype.yml`, is commented out; that file records it was replaced by a
  directory scan because Docker Hub is no longer configured.
- Individual service repos like Engine, Backend-API, Frontend, and Security have mirrored deployment artifacts.

## Contribution Guidelines  
- Only merges from `staging` occur into `main`, following stringent review and testing.  
- Emergency fixes require expedited team approval and follow strict policies.  
- All merges are subject to passing full CI/CD and security gating.

## Contact & Support  
For production deployment queries:  
- Open a GitHub issue. There is no GCP integration to route these to: the only workflow
  that still references GCP is `ops.collector.yml`, which is hard-disabled (`if: false`)
  because it used a long-lived service-account key.
- Report critical issues with the `main` branch on GitHub with relevant tags.
