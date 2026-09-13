"""Smoke tests for public (unauthenticated) endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_public_endpoint_returns_200(client_factory) -> None:
    client: AsyncClient = client_factory(None)
    async with client:
        response = await client.get("/v1/test/public")

    assert response.status_code == 200
    body = response.json()
    assert body["requires_auth"] is False
    assert "message" in body
