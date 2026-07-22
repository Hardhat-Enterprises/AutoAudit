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
