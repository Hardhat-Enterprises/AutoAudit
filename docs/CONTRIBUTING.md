# Contributing to AutoAudit

This guide helps you find the right area to contribute based on your skills and interests. AutoAudit is a monorepo with several modules, and you don't necessarily need to understand the whole system to make meaningful contributions.

## Project Overview

AutoAudit is a compliance automation platform for cloud environments. It collects configuration data from cloud services, evaluates it against compliance frameworks (like CIS benchmarks), and presents findings through a dashboard. The platform is built around these core components:

- A REST API that handles authentication and orchestrates scans
- A scanning engine that collects data and evaluates compliance policies
- A frontend dashboard for viewing results
- Infrastructure for deployment and monitoring

## Module Guide

### Backend API

**Location**: `/backend-api`

**What it does**: The backend API is the central hub of the application. It handles user authentication, manages tenants and scans, serves compliance results to the frontend, and coordinates with the scanning engine.

**Tech stack**:
- Python 3.10+
- FastAPI with Pydantic for request/response validation
- SQLAlchemy 2.0+ with async PostgreSQL
- FastAPI-Users for JWT authentication
- Alembic for database migrations

**Good fit if you**:
- Have Python experience and want to work on web APIs
- Are interested in authentication systems and RBAC
- Want to learn FastAPI and modern Python async patterns
- Enjoy designing database schemas and writing migrations

**Key directories**:
- `app/api/v1/` - API endpoint handlers
- `app/models/` - SQLAlchemy database models
- `app/schemas/` - Pydantic request/response schemas
- `app/services/` - Business logic layer
- `app/core/` - Configuration, auth, and middleware

**Getting started**: See `/backend-api/README.md` for setup instructions and examples of securing endpoints.

---

### Frontend

**Location**: `/frontend`

**What it does**: The frontend is a React dashboard that displays compliance scan results, visualizes data through charts, and provides the user interface for managing scans and settings.

**Tech stack**:
- React 19
- Tailwind CSS for styling
- React Router for navigation
- Chart.js for data visualization

**Good fit if you**:
- Have JavaScript/TypeScript and React experience
- Are interested in data visualization and dashboards
- Want to improve UX and design user-friendly interfaces
- Enjoy working with component libraries and styling systems

**Key directories**:
- `src/components/` - Reusable UI components
- `src/pages/` - Route-level page components
- `src/services/` - API client and data fetching

**Note**: The frontend currently uses mock data in some areas. Connecting it to the live backend API is ongoing work.

---

### Engine

**Location**: `/engine`

**What it does**: The engine is the compliance brain of the platform. It contains data collectors that fetch configuration from cloud APIs, and Rego policies that evaluate whether that configuration meets compliance standards.

**Tech stack**:
- Python for data collectors
- Open Policy Agent (OPA) for policy evaluation
- Rego policy language
- Microsoft Graph API client

**Good fit if you**:
- Are interested in cloud security and compliance
- Want to learn policy-as-code with OPA and Rego
- Have experience with cloud platforms (Azure, M365, GCP)
- Enjoy working with APIs and data transformation

**Key directories**:
- `collectors/` - Data collectors for cloud APIs (see `/engine/collectors/README.md`)
- `policies/` - Rego policies organized by framework (see `/engine/policies/README.md`)

**Getting started**: The engine has detailed documentation for writing new collectors and policies. Start with the READMEs in the `/engine/collectors/` and `/engine/policies/` directories.

---

### Infrastructure

**Location**: `/infrastructure`

**What it does**: Contains monitoring configuration, deployment infrastructure, and operational tooling for the platform.

**NB:** AutoAudit currently doesn't have any configured infrastructure to deploy to, so the deployment part of this is conceptual at present. As a result, the monitoring and alerting is also conceptual.

**Tech stack**:
- Docker and Docker Compose
- Monitoring tools
- CI/CD pipelines (GitHub Actions in `/.github/workflows`)

**Good fit if you**:
- Have DevOps or platform engineering experience
- Are interested in monitoring, alerting, and observability
- Want to work on deployment automation and CI/CD
- Enjoy containerization and infrastructure-as-code

**Key areas**:
- `monitoring/` - Monitoring and alerting configuration
- Root `docker-compose.yml` - Local development environment
- `/.github/workflows/` - CI/CD pipeline definitions

---

## Git Workflow

We use a simple branch-based workflow:

1. **Create a feature branch from main**
   ```bash
   git checkout main
   git pull origin main
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes and commit**
   ```bash
   git add .
   git commit -m "Add description of your changes"
   ```

3. **Push your branch**
   ```bash
   git push origin feature/your-feature-name
   ```

4. **Open a Pull Request** against the `main` branch on GitHub

### Branch naming

Use descriptive branch names that indicate what you're working on:
- `feature/add-user-roles` - New functionality
- `hotfix/login-redirect-bug` - Bug fixes
- `docs/update-readme` - Documentation changes
- `refactor/cleanup-api-routes` - Code improvements

## Pull Request Guidelines

Good pull requests make the review process smoother for everyone:

- **Keep them focused** - One PR should do one thing. If you find yourself writing "and" in the description, consider splitting it up.

- **Write a clear description** - Explain what the change does and why. Include screenshots for UI changes.

- **Test your changes** - Run tests locally before pushing. If you're adding new functionality, add tests for it.

- **Update documentation** - If your change affects how something works, update the relevant docs.

- **Respond to feedback** - Reviewers may request changes. Address them or explain why you disagree.

## Where to Get Help

- **Microsoft Planner items** - Check what's on the board, add tasks for things you're working on and keep them updated so the team is aware
- **Code Review** - Ask questions in your PR if you're unsure about something
- **Team Leads** - Reach out to the relevant module or team lead for guidance

