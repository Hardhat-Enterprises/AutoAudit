"""Smoke tests for authenticated endpoints."""

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
