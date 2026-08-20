"""Shared fixtures for backend-api tests."""

from __future__ import annotations

from collections.abc import AsyncGenerator, Callable
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.api.v1 import auth, contact, platforms, settings, test as test_routes
from app.core.auth import get_current_user
from app.db.session import get_async_session
from app.models.contact import ContactSubmission
from app.models.user import Role, User
from app.models.user_settings import UserSettings

# Minimal app: mount lightweight routers (avoid evidence/OCR import chain).
test_app = FastAPI()
test_app.include_router(test_routes.router, prefix="/v1")
test_app.include_router(auth.router, prefix="/v1")
test_app.include_router(settings.router, prefix="/v1")
test_app.include_router(contact.router, prefix="/v1")
test_app.include_router(platforms.router, prefix="/v1")


def make_user(*, role: str, user_id: int = 1) -> User:
    """Build an in-memory User for dependency overrides (no DB)."""
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
