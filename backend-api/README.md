# AutoAudit API

Automated GCP compliance assessment tool built with FastAPI. This API provides authentication and compliance assessment capabilities for GCP environments.

## 🚀 Quick Start

### Prerequisites

- Python 3.10 or higher
- [uv](https://github.com/astral-sh/uv) package manager

### Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/Hardhat-Enterprises/AutoAudit.git
   cd AutoAudit/backend-api
   ```

2. **Install dependencies using uv**

   ```bash
   uv sync
   ```

3. **Set up environment variables**

   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Run the development server**

   ```bash
   uv run uvicorn app.main:app --reload --port 8000
   ```

5. **Access the API**
   - API Documentation: http://localhost:8000/docs | http://localhost:8000/redoc
   - Root Endpoint: http://localhost:8000/

## Running tests

Install test tooling via the `dev` extra (not included in a plain `uv sync`):

```bash
uv sync --extra dev
```

Run the pytest suite from `backend-api/`:

```bash
uv run pytest tests/ -q
```

Use `-v` instead of `-q` for more detail. CI runs the same install and test commands on changes under `backend-api/**`.

## 🐳 Docker Startup and Database Migrations

When running the backend using the project's Docker configuration, the container starts through `backend-api/entrypoint.sh`.

The startup sequence is:

1. Apply any pending database migrations:

   ```bash
   uv run alembic upgrade head
   ```

2. Seed the default administrator account:

   ```bash
   uv run python -m app.db.init_db
   ```

3. Start the FastAPI application:

   ```bash
   uv run uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```

This ensures that the database schema is updated before the backend application starts when using the Docker container.

### Future DevSecOps Improvement

The current implementation executes database migrations during container startup, which is suitable for local development and single-container deployments.

For future production environments using multiple replicas or rolling deployments, database migrations should be enforced as a dedicated deployment or pipeline step before updated application containers receive traffic. This reduces the risk of multiple containers attempting migrations simultaneously and provides a safer deployment process.
## 📁 Project Structure

```
backend-api/
├── app/
│   ├── api/
│   │   └── v1/               # Public + private endpoints
│   │
│   ├── core/                 # Config, logging, errors
│   │
│   ├── models/               # Pydantic DTOs
│   │
│   ├── services/             # Storage, CE adapter
│   │
│   └── main.py               # FastAPI app
│
├── tests/                    # Pytest suite (fixtures + endpoint tests)
│
├── .env.example              # Environment variables template
├── pyproject.toml            # Project dependencies & metadata
├── README.md
└── uv.lock                   # Lock file
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b your-name/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`). Please follow [Conventional Commits](https://www.conventionalcommits.org)
4. Push to the branch (`git push origin your-name/amazing-feature`)
5. Open a Pull Request

## Securing endpoints

Here's a quick guide to requiring authentication and authorization to FastAPI endpoints.
While we often use the spelling 'authorisation', if we stick to authorization then we'll avoid potential issues with official header names and keep things consistent.

If you have a look at the endpoints in `backend-api/app/api/v1/test.py` you'll find that there are function parameters that do the heavy lifting for us. There are a few functions that we reuse, such as `get_current_user`, `require_admin` and others.

If all we need to do is enforce authentication on an endpoint and not care about a user's role, we use a parameter with `Depends(get_current_user)`, like this:

```
  from app.core.auth import get_current_user
  from app.models.user import User

  @router.get("/some-authenticated-route")
  async def protected_endpoint1(current_user: User = Depends(get_current_user)):
      # Only authenticated users can access this
      return {"message": "This requires auth"}
```

If we want to add `authorization` into the mix (verifying a user has not only logged in but holds a particular role), then we use a function that's been written to check for a specific role, like `require_admin`. We'd use that like so:

```
  from app.core.auth import get_current_user
  from app.core.permissions import require_admin
  from app.models.user import User

  @router.get("/admin-only")
  async def admin_endpoint(current_user: User = Depends(require_admin)):
      # Only users with 'admin' role can access this
      # Any users that don't have this role will get a HTTP 403 Forbidden in response
      return {"message": "Yes, you have admin."}
```
