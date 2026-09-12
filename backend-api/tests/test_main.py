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
