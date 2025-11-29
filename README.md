# AutoAudit Monorepo - Dev Branch

## Project Overview
The dev branch is the active development and integration branch where all team members collaborate and contribute new features. Code here undergoes continuous testing, linting, and security analysis to ensure quality before promotion.

## Repository Structure
The repo remains organized into top-level folders by team:

- `/backend-api` - FastAPI backend with authentication
- `/security` - Evidence Assistant and TPRM Scanner
- `/frontend` - React dashboard
- `/engine` - Compliance scanning engine
- `/.github/workflows` - CI/CD pipelines

Full commit history and traceability from forks have been preserved.

## Local Development Setup
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
   docker compose up -d
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

## Docker Builds
- Teams with Docker Builds can access their updated images after a PR at our Docker Hub.
- Builds pushed are respective per environment, e.g; this dev branch will push to the :dev tag in the docker hub repo after the team name.
- Docker Hub: https://hub.docker.com/u/autoauditservices
- Engine Repo: https://hub.docker.com/r/autoauditservices/engine
- Backend-API Repo: https://hub.docker.com/r/autoauditservices/backend-api
- Frontend Repo: https://hub.docker.com/r/autoauditservices/frontend (not configured)
- Security Repo: https://hub.docker.com/r/autoauditservices/security (not configured)

## Contribution Guidelines
- Work within your designated team folder, keeping code modular and isolated.
- Follow project code style guides (enforced via automated linting/CI).
- All PRs must target the correct integration branch and include a clear description and relevant issue/PR references.
- Tag your team and relevant reviewers for all non-trivial work.

## Other Handy Tools
For testing the backend API, [Postman](https://www.postman.com/) is well worth downloading. At its most basic level, it allows us to send requests to the API and view the response when it comes back. More advanced usage can include tests (like expected results testing) and much more - it's worth getting if you're going to work on the backend or even interact with it from a frontend perspective.

## Contact & Support
For support or questions, please:
- Reach out to the DevOps lead for pipeline or environment questions.
- Open issues with appropriate tags for tracking.
