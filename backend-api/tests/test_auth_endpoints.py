"""Smoke tests for authenticated / authz endpoints."""

import pytest
from httpx import AsyncClient

from app.models.user import User


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
