"""Smoke tests for public and health endpoints."""

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.api.health import router as health_router


@pytest.mark.asyncio
async def test_public_endpoint_returns_200(client_factory) -> None:
    client: AsyncClient = client_factory(None)

    async with client:
        response = await client.get("/v1/test/public")

    assert response.status_code == 200
    body = response.json()
    assert body["requires_auth"] is False
    assert "message" in body


@pytest.mark.asyncio
async def test_liveness_endpoint_returns_healthy() -> None:
    test_app = FastAPI()
    test_app.include_router(health_router)

    transport = ASGITransport(app=test_app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:
        response = await client.get("/liveness")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}