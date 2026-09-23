"""Smoke tests for create_app without importing the evidence/OCR stack."""

from __future__ import annotations

import sys
import types

import pytest
from fastapi import APIRouter
from httpx import ASGITransport, AsyncClient


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


@pytest.mark.asyncio
async def test_create_app_root_and_liveness(main_module) -> None:
    app = main_module.create_app()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        root = await client.get("/")
        live = await client.get("/liveness")

    assert root.status_code == 200
    assert root.json()["status"] == "ok"
    assert live.status_code == 200
    assert live.json()["status"] == "healthy"


@pytest.mark.asyncio
async def test_metrics_requires_authentication(main_module) -> None:
    """/metrics exposes internal request/latency data and must not be public.

    Regression test for the review finding on PR #350: the endpoint was
    reachable by anyone with no authentication at all. It's now gated
    behind current_active_superuser, so both an anonymous request and one
    with a garbage/invalid session cookie must be rejected with 401
    *before* touching the database (no DB is configured in this test).
    """
    app = main_module.create_app()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        anonymous = await client.get("/metrics")
        invalid_cookie = await client.get(
            "/metrics", cookies={"autoaudit_jwt": "not-a-real-jwt"}
        )

    assert anonymous.status_code == 401
    assert invalid_cookie.status_code == 401
