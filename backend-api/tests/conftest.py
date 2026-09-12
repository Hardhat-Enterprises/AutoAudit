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
# Benchmark metadata (policies/{framework}/{benchmark}/{version}/metadata.json)
# lives in the repo at engine/policies, and is read straight off disk by
# BenchmarkFileReader. The app's own default, POLICIES_DIR=/app/policies, is
# a container path that only exists inside the Docker image -- it isn't
# present on a CI runner or a developer's machine running `uv run pytest`
# directly, so point at the real, checked-in policies directory instead.
os.environ.setdefault(
    "POLICIES_DIR", str(Path(__file__).resolve().parents[2] / "engine" / "policies")
)
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
# Shared fixtures for backend-api tests.

from collections.abc import AsyncGenerator, Callable
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.api.v1 import (
    auth,
    benchmarks,
    contact,
    m365_connections,
    manual_verification,
    platforms,
    scans,
    settings,
    test as test_routes,
)
from app.core.auth import get_current_user
from app.db.session import get_async_session
from app.models.contact import ContactSubmission, SubmissionHistory, SubmissionNote
from app.models.compliance import Scan
from app.models.m365_connection import M365Connection
from app.models.manual_scan_result_detail import ManualScanResultDetail
from app.models.scan_result import ScanResult
from app.models.user import Role, User
from app.models.user_settings import UserSettings

AUDITOR_FORBIDDEN_DETAIL = "Auditor or Admin access required"

# Minimal app: mount routers needed by the suite (avoid evidence/OCR import chain).
test_app = FastAPI()
test_app.include_router(test_routes.router, prefix="/v1")
test_app.include_router(auth.router, prefix="/v1")
test_app.include_router(settings.router, prefix="/v1")
test_app.include_router(contact.router, prefix="/v1")
test_app.include_router(platforms.router, prefix="/v1")
test_app.include_router(benchmarks.router, prefix="/v1")
test_app.include_router(manual_verification.router, prefix="/v1")
test_app.include_router(scans.router, prefix="/v1")
test_app.include_router(m365_connections.router, prefix="/v1")


def make_user(*, role: str, user_id: int = 1) -> User:
    user = User()
    user.id = user_id
    user.email = f"{role}-test@example.com"
    user.hashed_password = "unused"
    user.role = role
    user.is_active = True
    user.is_superuser = False
    user.is_verified = False
    user.first_name = None
    user.last_name = None
    user.organization_name = None
    return user


def _utcnow() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


@pytest.fixture
def viewer_user() -> User:
    return make_user(role=Role.VIEWER.value)


@pytest.fixture
def admin_user() -> User:
    return make_user(role=Role.ADMIN.value, user_id=2)


@pytest.fixture
def auditor_user() -> User:
    return make_user(role=Role.AUDITOR.value, user_id=3)


def _make_execute_result(items: list | None = None, single=None):
    result = MagicMock()
    scalars = MagicMock()
    scalars.all.return_value = items or []
    scalars.one_or_none.return_value = single
    result.scalars.return_value = scalars
    result.unique.return_value = result
    result.scalar_one_or_none.return_value = single
    return result


async def _populate_on_refresh(obj) -> None:
    """Fill server-default-like fields so response models can serialize."""
    now = _utcnow()
    if isinstance(obj, UserSettings):
        if getattr(obj, "id", None) is None:
            obj.id = 1
        if getattr(obj, "confirm_delete_enabled", None) is None:
            obj.confirm_delete_enabled = True
        if getattr(obj, "created_at", None) is None:
            obj.created_at = now
        if getattr(obj, "updated_at", None) is None:
            obj.updated_at = now
    elif isinstance(obj, ContactSubmission):
        if getattr(obj, "id", None) is None:
            obj.id = uuid4()
        if not getattr(obj, "status", None):
            obj.status = "new"
        if not getattr(obj, "priority", None):
            obj.priority = "medium"
        if getattr(obj, "created_at", None) is None:
            obj.created_at = now
        if getattr(obj, "updated_at", None) is None:
            obj.updated_at = now
    elif isinstance(obj, SubmissionNote):
        if getattr(obj, "id", None) is None:
            obj.id = uuid4()
        if getattr(obj, "created_at", None) is None:
            obj.created_at = now
        if getattr(obj, "updated_at", None) is None:
            obj.updated_at = now
    elif isinstance(obj, SubmissionHistory):
        if getattr(obj, "id", None) is None:
            obj.id = uuid4()
        if getattr(obj, "created_at", None) is None:
            obj.created_at = now
    elif isinstance(obj, ManualScanResultDetail):
        if getattr(obj, "id", None) is None:
            obj.id = 1
        if getattr(obj, "created_at", None) is None:
            obj.created_at = now
        if getattr(obj, "updated_at", None) is None:
            obj.updated_at = now
    elif isinstance(obj, M365Connection):
        if getattr(obj, "id", None) is None:
            obj.id = 1
        if getattr(obj, "is_active", None) is None:
            obj.is_active = True
        if getattr(obj, "created_at", None) is None:
            obj.created_at = now
        if getattr(obj, "updated_at", None) is None:
            obj.updated_at = now
    elif isinstance(obj, Scan):
        if getattr(obj, "id", None) is None:
            obj.id = 1
        if getattr(obj, "started_at", None) is None:
            obj.started_at = now
        if getattr(obj, "passed_count", None) is None:
            obj.passed_count = 0
        if getattr(obj, "failed_count", None) is None:
            obj.failed_count = 0
        if getattr(obj, "skipped_count", None) is None:
            obj.skipped_count = 0
        if getattr(obj, "error_count", None) is None:
            obj.error_count = 0
    elif isinstance(obj, ScanResult):
        if getattr(obj, "id", None) is None:
            obj.id = 1
        if getattr(obj, "created_at", None) is None:
            obj.created_at = now
        if getattr(obj, "updated_at", None) is None:
            obj.updated_at = now


@pytest.fixture
def mock_db_session() -> AsyncMock:
    """Async SQLAlchemy session stub for routes that Depend(get_async_session)."""
    session = AsyncMock()
    session.execute = AsyncMock(return_value=_make_execute_result())
    session.commit = AsyncMock()
    session.refresh = AsyncMock(side_effect=_populate_on_refresh)
    session.flush = AsyncMock()
    session.add = MagicMock()
    session.delete = AsyncMock()
    session.get = AsyncMock(return_value=None)
    return session


@pytest.fixture
def client_factory(
    mock_db_session: AsyncMock,
) -> Callable[[User | None], AsyncClient]:
    """Build an AsyncClient with optional authenticated user + mocked DB.

    Pass ``user=None`` for anonymous requests (no get_current_user override).
    """

    def _factory(user: User | None = None) -> AsyncClient:
        async def override_get_async_session() -> AsyncGenerator[AsyncMock, None]:
            yield mock_db_session

        test_app.dependency_overrides[get_async_session] = override_get_async_session

        if user is not None:
            # Bind to a non-optional local so mypy accepts the nested override return type.
            current_user: User = user

            async def override_get_current_user() -> User:
                return current_user

            test_app.dependency_overrides[get_current_user] = override_get_current_user
        else:
            test_app.dependency_overrides.pop(get_current_user, None)

        transport = ASGITransport(app=test_app)
        return AsyncClient(transport=transport, base_url="http://test")

    return _factory


@pytest.fixture(autouse=True)
def clear_dependency_overrides():
    yield
    test_app.dependency_overrides.clear()
