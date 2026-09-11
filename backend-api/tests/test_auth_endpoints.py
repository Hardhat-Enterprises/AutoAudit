"""Smoke tests for authenticated / authz endpoints."""

from collections.abc import AsyncGenerator
from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient

from app.core.auth import get_current_user
from app.models.user import User


@pytest.mark.asyncio
async def test_get_current_user_returns_user(viewer_user: User) -> None:
    assert await get_current_user(viewer_user) is viewer_user


@pytest.mark.asyncio
async def test_users_me_returns_200_with_overridden_user(
    client_factory,
    viewer_user: User,
) -> None:
    client: AsyncClient = client_factory(viewer_user)
    async with client:
        response = await client.get("/v1/auth/users/me")

    assert response.status_code == 200
    body = response.json()
    assert body["email"] == viewer_user.email
    assert body["role"] == viewer_user.role
    assert body["id"] == viewer_user.id


@pytest.mark.asyncio
async def test_users_me_returns_401_without_auth(client_factory) -> None:
    """Protected /users/me must reject anonymous requests."""
    client: AsyncClient = client_factory(None)
    async with client:
        response = await client.get("/v1/auth/users/me")

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_users_me_returns_401_with_invalid_token(client_factory) -> None:
    """Protected /users/me must reject an invalid Bearer token."""
    client: AsyncClient = client_factory(None)
    async with client:
        response = await client.get(
            "/v1/auth/users/me",
            headers={"Authorization": "Bearer not-a-valid-jwt"},
        )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_update_users_me(
    client_factory,
    mock_db_session: AsyncMock,
    viewer_user: User,
) -> None:
    mock_db_session.get = AsyncMock(return_value=viewer_user)

    async def fake_session() -> AsyncGenerator[AsyncMock, None]:
        yield mock_db_session

    with patch("app.db.session.get_async_session", fake_session):
        client: AsyncClient = client_factory(viewer_user)
        async with client:
            response = await client.patch(
                "/v1/auth/users/me",
                json={
                    "first_name": "Ada",
                    "last_name": "Lovelace",
                    "organization_name": "Analytical Engines",
                },
            )

    assert response.status_code == 200
    assert viewer_user.first_name == "Ada"
    assert viewer_user.last_name == "Lovelace"
    assert viewer_user.organization_name == "Analytical Engines"
    mock_db_session.commit.assert_awaited()


@pytest.mark.asyncio
async def test_update_users_me_not_found(
    client_factory,
    mock_db_session: AsyncMock,
    viewer_user: User,
) -> None:
    mock_db_session.get = AsyncMock(return_value=None)

    async def fake_session() -> AsyncGenerator[AsyncMock, None]:
        yield mock_db_session

    with patch("app.db.session.get_async_session", fake_session):
        client: AsyncClient = client_factory(viewer_user)
        async with client:
            response = await client.patch(
                "/v1/auth/users/me",
                json={"first_name": "Ada"},
            )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_users_me_partial_fields(
    client_factory,
    mock_db_session: AsyncMock,
    viewer_user: User,
) -> None:
    """Only first_name set — last_name/organization branches should be skipped."""
    viewer_user.first_name = "Old"
    viewer_user.last_name = "Keep"
    viewer_user.organization_name = "KeepOrg"
    mock_db_session.get = AsyncMock(return_value=viewer_user)

    async def fake_session() -> AsyncGenerator[AsyncMock, None]:
        yield mock_db_session

    with patch("app.db.session.get_async_session", fake_session):
        client: AsyncClient = client_factory(viewer_user)
        async with client:
            response = await client.patch(
                "/v1/auth/users/me",
                json={"first_name": "New"},
            )

    assert response.status_code == 200
    assert viewer_user.first_name == "New"
    assert viewer_user.last_name == "Keep"
    assert viewer_user.organization_name == "KeepOrg"


@pytest.mark.asyncio
async def test_protected_endpoint_returns_200_for_viewer(
    client_factory,
    viewer_user: User,
) -> None:
    client: AsyncClient = client_factory(viewer_user)
    async with client:
        response = await client.get("/v1/test/protected")

    assert response.status_code == 200
    body = response.json()
    assert body["requires_auth"] is True
    assert body["user"]["email"] == viewer_user.email


@pytest.mark.asyncio
async def test_admin_endpoint_forbidden_for_viewer(
    client_factory,
    viewer_user: User,
) -> None:
    client: AsyncClient = client_factory(viewer_user)
    async with client:
        response = await client.get("/v1/test/protected-admin")

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_admin_endpoint_ok_for_admin(
    client_factory,
    admin_user: User,
) -> None:
    client: AsyncClient = client_factory(admin_user)
    async with client:
        response = await client.get("/v1/test/protected-admin")

    assert response.status_code == 200
    assert response.json()["requires_role"] == "admin"


@pytest.mark.asyncio
async def test_auditor_endpoint_forbidden_for_viewer(
    client_factory,
    viewer_user: User,
) -> None:
    client: AsyncClient = client_factory(viewer_user)
    async with client:
        response = await client.get("/v1/test/protected-auditor")

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_auditor_endpoint_ok_for_auditor(
    client_factory,
    auditor_user: User,
) -> None:
    client: AsyncClient = client_factory(auditor_user)
    async with client:
        response = await client.get("/v1/test/protected-auditor")

    assert response.status_code == 200
