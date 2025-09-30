# 📘 AutoAudit Backend

The **AutoAudit Backend** project provides the core backend infrastructure for the AutoAudit system. It is responsible for:

- 🗄️ Centralized **PostgreSQL database** for all AutoAudit services
- ⚡ **Redis caching** for fast access and task queuing
- 🐳 Backend services containerized with **Docker**
- 🔗 Integration with other AutoAudit components (API, Frontend, etc.)

This repository serves as the **foundation** for all AutoAudit services to build upon.

---

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose installed
- Git installed
- Basic understanding of containers

### Installation

Clone the repository:

```bash
git clone https://github.com/Hardhat-Enterprises/autoaudit-backend.git
cd autoaudit-backend
```

Start the services using Docker Compose:

```bash
docker-compose up --build
```

This will start:

- 🐘 PostgreSQL database on **port 5432**
- 🔴 Redis server on **port 6379**
- ⚙️ FastAPI backend on **port 8000**

---

## 📁 Project Structure

```
autoaudit-backend/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py               # FastAPI entry point
│   │   ├── models/               # Database models
│   │   ├── routes/               # API routes for backend services
│   │   └── utils/                # Utility functions
│   │
│   └── requirements.txt          # Python dependencies
│
├── db/
│   └── autoaudit_schema.sql      # Common database schema
│
├── docker-compose.yml            # Multi-service container setup
├── Dockerfile                    # Backend service container build
├── .env.example                  # Environment variables template
└── README.md
```

---

## ⚙️ Environment Variables

Copy `.env.example` to `.env` and configure:

```env
DATABASE_URL=postgresql://postgres:postgres@db:5432/autoaudit
REDIS_URL=redis://redis:6379/0
```

---

## 🔍 Access

- Swagger UI → [http://localhost:8000/docs](http://localhost:8000/docs)
- PostgreSQL → `localhost:5432`
- Redis → `localhost:6379`

---

## 🧪 Development Workflow

Pull latest changes:

```bash
git pull origin main
```

Work in a feature branch:

```bash
git checkout -b feature/your-feature
```

Add & commit changes:

```bash
git add .
git commit -m "feat: added authentication service"
```

Push to GitHub:

```bash
git push origin feature/your-feature
```

---

## 🤝 Contributing

1. Fork the repository
2. Create a new branch → `git checkout -b feature/your-feature`
3. Commit your changes (use [Conventional Commits](https://www.conventionalcommits.org/))
4. Push to your fork and open a Pull Request

---

## Database Authentication

A new schema file was added: **db/auth_schema.sql**

This introduces **database-native authentication** to AutoAudit:

- `auth.users` → manages registered users with bcrypt-hashed passwords (`pgcrypto/crypt()`)
- `auth.refresh_tokens` → manages session tokens (issue, validate, revoke)

### Example Flows

The schema includes ready-to-run SQL examples for:

1. **Sign-up** - register a user with secure password hashing
2. **Sign-in** - verify credentials using PostgreSQL `crypt()`
3. **Update last login** - record timestamp of user activity
4. **Issue tokens** - generate refresh tokens for 60 days
5. **Validate tokens** - check if sessions are active
6. **Revoke tokens** - handle logout and forced invalidation

### How to run

Apply the schema in PostgreSQL:

```bash
psql "$DATABASE_URL" -f db/auth_schema.sql
```
