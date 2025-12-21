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

### When You Complete a Component

This section explains what you need to update when you finish work on different parts of the compliance engine. Following these steps ensures your work is properly integrated and can be used in scans.

#### Completing a Collector

When you finish implementing a data collector:

1. **Register the collector** in `engine/collectors/registry.py`:
   ```python
   from engine.collectors.entra.my_domain.my_collector import MyCollector

   DATA_COLLECTORS: dict[str, type[BaseDataCollector]] = {
       # ... existing collectors ...
       "entra.my_domain.my_collector": MyCollector,
   }
   ```

2. **Update metadata.json** for the benchmark version you're implementing:
   - Set `data_collector_id` to your collector's registry ID
   - Change `automation_status` from `not_started` to `ready` (or `deferred`/`blocked` with notes if applicable)

   File: `engine/policies/cis/microsoft-365-foundations/vX.X.X/metadata.json`

3. **Update the controls documentation**:
   - Set the Status column to "Automated" or "Deferred"
   - Add the Collector ID

   File: `docs/engine/policies/cis/microsoft-365-foundations/vX.X.X/controls.md`

4. **Document your collector output** in the analysis document:
   - Add example JSON output
   - Note what the OPA policy can evaluate

   File: `docs/engine/cis-m365-v6-collectors-analysis.md`

5. **Test your collector** against a live M365 tenant (see Testing Your Collector below)

#### Testing Your Collector

Use the collector test script to verify your collector works against a live M365 tenant.

**Step 1: Set environment variables**

You need to configure credentials for your M365 app registration before running the test script.

**macOS / Linux:**
```bash
export M365_TENANT_ID=your-tenant-id-here
export M365_CLIENT_ID=your-client-id-here
export M365_CLIENT_SECRET=your-client-secret-here
```

**Windows (PowerShell):**
```powershell
$env:M365_TENANT_ID = "your-tenant-id-here"
$env:M365_CLIENT_ID = "your-client-id-here"
$env:M365_CLIENT_SECRET = "your-client-secret-here"
```

**Step 2: Run the test script**

**macOS / Linux:**
```bash
cd engine

# List available collectors
python -m scripts.test_collector --list

# Test a specific collector
python -m scripts.test_collector -c entra.roles.cloud_only_admins

# Test and save output to a file
python -m scripts.test_collector -c entra.roles.cloud_only_admins -o ./samples/

# Test all collectors and generate summary report
python -m scripts.test_collector --all -o ./samples/
```

**Windows (PowerShell):**
```powershell
cd engine

# List available collectors
python -m scripts.test_collector --list

# Test a specific collector
python -m scripts.test_collector -c entra.roles.cloud_only_admins

# Test and save output to a file
python -m scripts.test_collector -c entra.roles.cloud_only_admins -o .\samples\

# Test all collectors and generate summary report
python -m scripts.test_collector --all -o .\samples\
```

**What the test script does:**
- Authenticates to your M365 tenant using the provided credentials
- Runs the specified collector and captures the JSON output
- Reports elapsed time and any errors encountered
- Optionally saves results to a JSON file for documentation

#### Completing a Rego Policy

When you finish implementing a Rego policy:

1. **Ensure metadata annotations** are complete in the policy file:
   ```rego
   # METADATA
   # title: Short control name
   # description: What this control checks
   # custom:
   #   control_id: X.X.X
   #   framework: cis
   #   benchmark: microsoft-365-foundations
   #   version: vX.X.X
   #   severity: critical|high|medium|low
   #   service: EntraID|Exchange|SharePoint|Teams|etc
   #   requires_permissions:
   #   - Permission.Read.All
   ```

2. **Update metadata.json** for the benchmark version:
   - Set `policy_file` to your Rego file name

   File: `engine/policies/cis/microsoft-365-foundations/vX.X.X/metadata.json`

3. **Test the policy** with sample collector output using OPA eval.

#### When Both Collector and Policy are Ready

A control is scannable when both its collector and policy are implemented:

1. Set `automation_status` to `ready` in metadata.json
2. Update the controls.md Status column to "Automated"
3. Verify the control works end-to-end with the test harness

#### Control Metadata Schema

Each control in metadata.json uses this schema:

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `control_id` | string | Yes | Control ID without framework prefix (e.g., "1.1.1") |
| `title` | string | Yes | Control title |
| `description` | string | No | Control description |
| `severity` | string | No | critical, high, medium, low |
| `service` | string | No | EntraID, Exchange, SharePoint, Teams, etc. |
| `level` | string | Yes | "L1" or "L2" |
| `is_manual` | boolean | Yes | true if no API available |
| `benchmark_audit_type` | string | Yes | What the benchmark says: "Automated" or "Manual" |
| `automation_status` | string | Yes | ready, deferred, blocked, manual, not_started |
| `data_collector_id` | string | Nullable | Collector registry ID, null for manual |
| `policy_file` | string | Nullable | Rego policy filename, null for manual |
| `requires_permissions` | array | Nullable | Required API permissions |
| `notes` | string | Nullable | Blockers, special considerations |

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

