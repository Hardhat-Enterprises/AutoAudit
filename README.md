# AutoAudit Monorepo - Main/Deployment Branch

## Project Overview
AutoAudit is a M365 compliance automation platform built by several specialist teams. This monorepo centralizes all codebases—including backend services, APIs, compliance scanners, and frontends—enabling unified CI/CD, streamlined development, and rapid automated deployments to the cloud.

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

### Local Development Setup
If you want to get the backend API running locally for development:

**Prerequisites**:
- **Python 3.10+**: Download from [python.org](https://www.python.org/downloads/)
- **Docker Desktop**: Download from [docker.com](https://www.docker.com/products/docker-desktop/)
- **uv** (Python package manager): Install using the command below

1. **Install uv** (if you don't have it already):

   On Windows (PowerShell):
   ```powershell
   iwr https://astral.sh/uv/install.ps1 | iex
   ```

   On macOS/Linux:
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. **Start the database** (PostgreSQL in Docker):
   ```bash
   docker compose -f docker-compose.dev.yml up -d
   ```
   This spins up a PostgreSQL instance on port 5432 with the dev credentials already configured.

3. **Set up the backend environment**:
   ```bash
   cd backend-api
   cp .env.example .env
   ```
   The default `.env` settings work out of the box with the Docker database.

4. **Install dependencies and run the API**:
   ```bash
   uv sync
   uv run uvicorn app.main:app --reload --port 8000
   ```

5. **Check it's working**:
   - API docs: http://localhost:8000/docs
   - Alternative docs: http://localhost:8000/redoc
   - The API includes test endpoints at `/api/v1/test/*` that demonstrate authentication patterns

**Note**: The backend uses FastAPI-users for authentication with JWT tokens. Check the interactive docs to try out the auth endpoints and see how to secure your own routes.

## Contribution Guidelines  
- Only merges from `staging` occur into `main`, following stringent review and testing.  
- Emergency fixes require expedited team approval and follow strict policies.  
- All merges are subject to passing full CI/CD and security gating.

## Contact & Support  
For production deployment queries:  
- Contact the DevOps lead managing GCP integration.  
- Report critical issues with `main` branch deployments on GitHub with relevant tags.

## Other handy tools
For testing the backend API, [Postman](https://www.postman.com/) is well worth downloading. At its most basic level, it allows us to send requests to the API and view the response when it comes back. More advanced usage can include tests (like expected results testing) and much more - but it's worth getting if you're going to work on the backend or even interact with it from a frontend perspective.