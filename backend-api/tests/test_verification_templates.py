"""Tests for verification template API endpoints."""

from unittest.mock import AsyncMock

import pytest
from app.models.user import User


@pytest.mark.asyncio
async def test_authenticated_user_gets_404_for_missing_template(
    client_factory,
    viewer_user: User,
):
    async with client_factory(viewer_user) as client:
        response = await client.get(
            "/v1/verification-templates/"
            "cis/microsoft-365/v6.0.0/1.1.1"
        )

    assert response.status_code == 404
    assert "not found" in response.json()["detail"]


@pytest.mark.asyncio
async def test_viewer_cannot_create_verification_template(
    client_factory,
    viewer_user: User,
):
    payload = {
        "framework": "cis",
        "benchmark": "microsoft-365",
        "version": "v6.0.0",
        "control_id": "1.1.1",
        "title": "Example verification",
        "instructions": "Check the configuration manually.",
        "keywords": ["manual", "verification"],
        "severity": "medium",
        "evidence_type": "screenshot",
    }

    async with client_factory(viewer_user) as client:
        response = await client.post(
            "/v1/verification-templates/",
            json=payload,
        )

    assert response.status_code == 403
    assert response.json()["detail"] == "Admin access required"


@pytest.mark.asyncio
async def test_admin_cannot_create_duplicate_verification_template(
    client_factory,
    admin_user: User,
    mock_db_session: AsyncMock,
):
    existing_template = object()
    mock_db_session.execute.return_value.scalar_one_or_none.return_value = (
        existing_template
    )

    payload = {
        "framework": "cis",
        "benchmark": "microsoft-365",
        "version": "v6.0.0",
        "control_id": "1.1.1",
        "title": "Example verification",
        "instructions": "Check the configuration manually.",
        "keywords": ["manual", "verification"],
        "severity": "medium",
        "evidence_type": "screenshot",
    }

    async with client_factory(admin_user) as client:
        response = await client.post(
            "/v1/verification-templates/",
            json=payload,
        )

    assert response.status_code == 409
    assert "already exists" in response.json()["detail"]