# Getting Started

This guide will help you get the AutoAudit development environment running on your machine. By the end, you'll have the full stack running locally and be ready to start contributing.

## Prerequisites

Before you begin, make sure you have the following installed:

- **Git** - For version control
- **Docker Desktop** - For running the development services
- **VS Code** (recommended) - Or your preferred editor

Depending on which module you'll be working on, you may also need:

- **Python 3.10+** and **uv** - For backend-api or engine work
- **Node.js 20+** and **npm** - For frontend work

## Clone the Repository

```bash
git clone https://github.com/Hardhat-Enterprises/AutoAudit.git
cd AutoAudit
```

## Quick Start with Docker

The fastest way to get everything running is with Docker Compose. This will start the full stack including the database, Redis, OPA, and all application services.

If you want to test **Google SSO** locally, create a `.env` file (gitignored) and set:

- `GOOGLE_OAUTH_CLIENT_ID`
- `GOOGLE_OAUTH_CLIENT_SECRET`

You can start from the template:

```bash
cp env.example .env
```

```bash
docker compose --profile all up --build -d
```

Once the containers are running:

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs
- OPA: http://localhost:8181

The backend automatically runs database migrations and seeds a default admin user on first startup:

- Email: `admin@example.com`
- Password: `admin`


### Infrastructure Only (default)

Starts the infrastructure services. Use this when you want to run both the frontend and backend locally.

```bash
docker compose up -d
```

Services started:
- PostgreSQL on port 5432
- Redis on port 6379
- OPA on port 8181

### Frontend Development

If you're working on the frontend and want the backend running in Docker:

```bash
docker compose --profile frontend-dev up -d
cd frontend
npm install
npm start
```

This starts the backend-api in Docker (port 8000), and you run the frontend locally (port 3000).

### Backend Development

If you're working on the backend and want the frontend running in Docker:

```bash
docker compose --profile backend-dev up -d
cd backend-api
uv sync
uv run uvicorn app.main:app --reload --port 8000
```

This starts the frontend in Docker (port 3000), and you run the backend locally (port 8000).

### Full Stack in Docker

For testing or demos, run everything in containers:

```bash
docker compose --profile all up -d
```

## Module-Specific Setup

If you're developing a specific module locally, here's how to set each one up.

### Backend API

The backend is a FastAPI application using Python and the uv package manager.

```bash
cd backend-api

# Install dependencies
uv sync

# Run database migrations
uv run alembic upgrade head

# Seed default admin user (optional, dev only)
uv run python -m app.db.init_db

# Start the development server with hot reload
uv run uvicorn app.main:app --reload --port 8000
```

The API documentation will be available at http://localhost:8000/docs.

Make sure PostgreSQL and Redis are running (via `docker compose up -d`) before starting the backend.

### Frontend

The frontend is a React application.

```bash
cd frontend

# Install dependencies
npm install

# Start the development server
npm start
```

The app will open at http://localhost:3000.

### Engine

The engine runs as the `worker` (Celery) service when you start the full stack with Docker Compose:

```bash
docker compose --profile all up --build -d
```

The worker logs are output directly to the Docker logs. You can view them with `docker compose logs -f worker`.

## Verifying Your Setup

Here's how to confirm everything is working:

1. **Database**: Connect to PostgreSQL at `localhost:5432` (user: `autoaudit`, password: `autoaudit_dev_password`, database: `autoaudit`)

2. **Backend API**: Visit http://localhost:8000/docs - you should see the Swagger UI

3. **Frontend**: Visit http://localhost:3000 - you should see the dashboard

4. **OPA**: Visit http://localhost:8181/health - you should get a healthy response

## Common Issues

**Port already in use**: Check if you have other services running on ports 3000, 5432, 6379, 8000, or 8181. Stop them or modify the ports in docker-compose.yml.

**Docker containers won't start**: Run `docker compose logs` to see error messages. Often it's a port conflict or insufficient resources allocated to Docker.

**Database connection errors**: Make sure the db container is healthy before starting the backend. Check with `docker compose ps`.

## Next Steps

Now that you're set up, head over to [CONTRIBUTING.md](./CONTRIBUTING.md) to learn about the different modules and find the right area to start contributing based on your skills and interests.
