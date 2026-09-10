"""Readiness endpoint tests without importing the evidence/OCR stack."""

from __future__ import annotations

import sys
import types

import pytest
from fastapi import APIRouter
from httpx import ASGITransport, AsyncClient

from app.db.session import get_async_session


@pytest.fixture
def main_module():
    """Import app.main with a stubbed API router (avoids evidence → pytesseract)."""
    stub = types.ModuleType("app.api.v1.router")
    stub.api_router = APIRouter()
    previous = sys.modules.get("app.api.v1.router")
    sys.modules["app.api.v1.router"] = stub
    sys.modules.pop("app.main", None)
    import app.main as main  # noqa: WPS433 — intentional late import after stub

    yield main

    sys.modules.pop("app.main", None)
    if previous is not None:
        sys.modules["app.api.v1.router"] = previous
    else:
        sys.modules.pop("app.api.v1.router", None)


class HealthySession:
    async def execute(self, statement):
        return None


class FailingSession:
    async def execute(self, statement):
        raise ConnectionError("Database unavailable")


async def healthy_session():
    yield HealthySession()


async def failing_session():
    yield FailingSession()


@pytest.mark.asyncio
async def test_readiness_when_database_available(main_module) -> None:
    app = main_module.create_app()
    app.dependency_overrides[get_async_session] = healthy_session

    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/readiness")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == {"status": "ready"}


@pytest.mark.asyncio
async def test_readiness_when_database_unavailable(main_module) -> None:
    app = main_module.create_app()
    app.dependency_overrides[get_async_session] = failing_session

    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/readiness")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 503
    assert response.json() == {"status": "not_ready"}
