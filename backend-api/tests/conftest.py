"""Shared fixtures for backend-api tests."""

from __future__ import annotations

from collections.abc import AsyncGenerator, Callable
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.api.v1 import m365_connections, scans
from app.core.auth import get_current_user
from app.db.session import get_async_session
from app.models.user import Role, User

AUDITOR_FORBIDDEN_DETAIL = "Auditor or Admin access required"

test_app = FastAPI()
test_app.include_router(scans.router, prefix="/v1")
test_app.include_router(m365_connections.router, prefix="/v1")


def make_user(*, role: str, user_id: int = 1) -> User:
    user = User()
    user.id = user_id
    user.email = f"{role}-test@example.com"
    user.role = role
    user.is_active = True
    user.is_superuser = False
    user.is_verified = False
    return user


@pytest.fixture
def viewer_user() -> User:
    return make_user(role=Role.VIEWER.value)


@pytest.fixture
def admin_user() -> User:
    return make_user(role=Role.ADMIN.value, user_id=2)


def _make_execute_result(items: list | None = None, single=None):
    result = MagicMock()
    scalars = MagicMock()
    scalars.all.return_value = items or []
    scalars.one_or_none.return_value = single
    result.scalars.return_value = scalars
    result.unique.return_value = result
    result.scalar_one_or_none.return_value = single
    return result


@pytest.fixture
def mock_db_session() -> AsyncMock:
    session = AsyncMock()
    session.execute = AsyncMock(return_value=_make_execute_result())
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    session.flush = AsyncMock()
    session.add = MagicMock()
    session.delete = AsyncMock()
    return session


@pytest.fixture
def client_factory(
    mock_db_session: AsyncMock,
) -> Callable[[User], AsyncClient]:
    def _factory(user: User) -> AsyncClient:
        async def override_get_current_user() -> User:
            return user

        async def override_get_async_session() -> AsyncGenerator[AsyncMock, None]:
            yield mock_db_session

        test_app.dependency_overrides[get_current_user] = override_get_current_user
        test_app.dependency_overrides[get_async_session] = override_get_async_session
        transport = ASGITransport(app=test_app)
        return AsyncClient(transport=transport, base_url="http://test")

    return _factory


@pytest.fixture(autouse=True)
def clear_dependency_overrides():
    yield
    test_app.dependency_overrides.clear()
