"""
Shared pytest fixtures for the AutoAudit backend-api integration test suite.

Design notes (why this file is structured the way it is):

- Environment variables MUST be set before `app.*` is imported anywhere,
  because `app/core/config.py` and `app/db/base.py` build a `Settings`
  instance and a SQLAlchemy engine at *module import time*, not lazily.
  If we imported the app first and set env vars after, the engine would
  already be bound to the wrong database.
- We point at a dedicated `autoaudit_test` database, never the real dev
  database, so running the suite locally can never touch real data.
- Each test runs inside its own outer transaction plus a SQLAlchemy
  savepoint (`join_transaction_mode="create_savepoint"`). App code calls
  `session.commit()` in several places (scan creation, evidence
  validation, user updates); with a plain transaction that commit would
  end the transaction early and break rollback-based isolation. Savepoint
  mode makes `commit()` release a SAVEPOINT instead, so the *outer*
  transaction can still be rolled back after the test to erase every
  change it made -- no manual cleanup or table truncation needed between
  tests.
"""
import base64
import os
import subprocess  # nosec B404 -- fixed, hardcoded alembic invocation below; no untrusted input
import sys
import uuid
from pathlib import Path

# ---------------------------------------------------------------------------
# Environment MUST be set before any `app.*` import below.
# ---------------------------------------------------------------------------
os.environ.setdefault(
    "DATABASE_URL",
    "postgresql+asyncpg://autoaudit:autoaudit_dev_password@localhost:5432/autoaudit_test",  # pragma: allowlist secret
)
os.environ.setdefault("SECRET_KEY", "test-secret-key-not-for-production")  # pragma: allowlist secret
os.environ.setdefault("BACKEND_PUBLIC_URL", "http://testserver")
os.environ.setdefault("FRONTEND_URL", "http://localhost:3000")
os.environ.setdefault("GOOGLE_OAUTH_CLIENT_ID", "test-client-id")
os.environ.setdefault("GOOGLE_OAUTH_CLIENT_SECRET", "test-client-secret")  # pragma: allowlist secret
os.environ.setdefault("REDIS_URL", "redis://localhost:6379")
os.environ.setdefault("OPA_URL", "http://localhost:8181")
# A deterministic, validly-formatted Fernet key (32 raw bytes, urlsafe
# base64-encoded). Computed rather than hand-typed so it can't be a subtly
# invalid string -- an invalid key raises immediately the first time any
# evidence-scan code path calls encrypt()/decrypt().
os.environ.setdefault("ENCRYPTION_KEY", base64.urlsafe_b64encode(b"0" * 32).decode())

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.db.base import engine
from app.db.session import get_async_session
from app.main import app

BACKEND_API_ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="session", autouse=True)
def _migrate_test_database():
    """Bring the test database schema up to date once per test run.

    Mirrors production exactly (see backend-api/entrypoint.sh):
    `uv run alembic upgrade head`. Safe to run repeatedly -- Alembic
    tracks the applied revision and no-ops once the schema is current, so
    this works whether the test DB is a fresh CI container or a
    developer's persistent local one.
    """
    subprocess.run(  # nosec B603 -- fixed argv list below, shell=False, no untrusted input
        [sys.executable, "-m", "alembic", "upgrade", "head"],
        cwd=BACKEND_API_ROOT,
        check=True,
    )


@pytest_asyncio.fixture
async def db_session():
    """A database session scoped to a single test.

    Everything the test (and the app code it exercises) does happens
    inside one outer transaction on a dedicated connection. Because the
    sessionmaker below joins that transaction in "create_savepoint" mode,
    the app's own `await session.commit()` calls release a SAVEPOINT
    instead of ending the outer transaction -- so rolling back the outer
    transaction after the test undoes everything, no matter how many
    times the app code committed.
    """
    async with engine.connect() as connection:
        await connection.begin()
        session_factory = async_sessionmaker(
            bind=connection,
            expire_on_commit=False,
            join_transaction_mode="create_savepoint",
        )
        async with session_factory() as session:
            yield session
        await connection.rollback()


@pytest_asyncio.fixture
async def client(db_session):
    """An httpx.AsyncClient wired directly into the FastAPI app in-process
    (no real network, no running server), with the database dependency
    overridden to use this test's isolated session.
    """

    async def _override_get_async_session():
        yield db_session

    app.dependency_overrides[get_async_session] = _override_get_async_session
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def registered_user(client):
    """Register a fresh, unique user via the real HTTP registration
    endpoint (not a shortcut DB insert), returning (email, password).
    """
    email = f"test-{uuid.uuid4().hex}@example.com"
    password = "Sup3r-Secret-Test-Pw!"  # nosec B105 # pragma: allowlist secret
    resp = await client.post(
        "/v1/auth/register",
        json={"email": email, "password": password},
    )
    assert resp.status_code == 201, resp.text  # nosec B101
    return email, password


@pytest_asyncio.fixture
async def auth_client(client, registered_user):
    """A client already logged in as `registered_user`, via the real
    cookie-based login endpoint. httpx.AsyncClient keeps its own cookie
    jar, so every request made with this client after login carries the
    `autoaudit_jwt` cookie automatically, exactly like a real browser.
    """
    email, password = registered_user
    resp = await client.post(
        "/v1/auth/login",
        data={"username": email, "password": password},
    )
    assert resp.status_code == 204, resp.text  # nosec B101
    return client