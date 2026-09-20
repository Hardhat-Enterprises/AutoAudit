"""Tests for benchmark discovery endpoints (mocked file reader)."""

from unittest.mock import MagicMock, patch

import pytest
from httpx import AsyncClient

from app.models.user import User

SAMPLE_BENCHMARK = {
    "framework": "cis",
    "slug": "microsoft-365-foundations",
    "version": "v3.1.0",
    "benchmark": "CIS Microsoft 365 Foundations",
    "platform": "m365",
    "release_date": "2024-01-01",
    "source_url": "https://example.com",
    "controls": [
        {
            "control_id": "CIS-1.1.1",
            "title": "Ensure MFA",
            "description": "Require MFA",
            "severity": "high",
            "service": "Entra",
            "level": "1",
            "is_manual": False,
            "benchmark_audit_type": "automated",
            "automation_status": "ready",
            "data_collector_id": None,
            "policy_file": "cis_1_1_1.rego",
            "requires_permissions": None,
            "notes": None,
        }
    ],
}


@pytest.mark.asyncio
async def test_list_benchmarks(
    client_factory,
    viewer_user: User,
) -> None:
    reader = MagicMock()
    reader.list_benchmarks.return_value = [SAMPLE_BENCHMARK]

    with patch("app.api.v1.benchmarks.get_file_reader", return_value=reader):
        client: AsyncClient = client_factory(viewer_user)
        async with client:
            response = await client.get("/v1/benchmarks")

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["slug"] == "microsoft-365-foundations"
    assert body[0]["control_count"] == 1


@pytest.mark.asyncio
async def test_get_benchmark_ok(
    client_factory,
    viewer_user: User,
) -> None:
    reader = MagicMock()
    reader.get_benchmark_metadata.return_value = SAMPLE_BENCHMARK

    with patch("app.api.v1.benchmarks.get_file_reader", return_value=reader):
        client: AsyncClient = client_factory(viewer_user)
        async with client:
            response = await client.get(
                "/v1/benchmarks/cis/microsoft-365-foundations/v3.1.0"
            )

    assert response.status_code == 200
    assert response.json()["framework"] == "cis"


@pytest.mark.asyncio
async def test_get_benchmark_not_found(
    client_factory,
    viewer_user: User,
) -> None:
    reader = MagicMock()
    reader.get_benchmark_metadata.side_effect = FileNotFoundError("missing")

    with patch("app.api.v1.benchmarks.get_file_reader", return_value=reader):
        client: AsyncClient = client_factory(viewer_user)
        async with client:
            response = await client.get("/v1/benchmarks/cis/missing/v1.0.0")

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_list_controls(
    client_factory,
    viewer_user: User,
) -> None:
    reader = MagicMock()
    reader.list_controls.return_value = SAMPLE_BENCHMARK["controls"]

    with patch("app.api.v1.benchmarks.get_file_reader", return_value=reader):
        client: AsyncClient = client_factory(viewer_user)
        async with client:
            response = await client.get(
                "/v1/benchmarks/cis/microsoft-365-foundations/v3.1.0/controls"
            )

    assert response.status_code == 200
    assert response.json()[0]["control_id"] == "CIS-1.1.1"


@pytest.mark.asyncio
async def test_get_control_ok(
    client_factory,
    viewer_user: User,
) -> None:
    reader = MagicMock()
    reader.get_control_metadata.return_value = SAMPLE_BENCHMARK["controls"][0]

    with patch("app.api.v1.benchmarks.get_file_reader", return_value=reader):
        client: AsyncClient = client_factory(viewer_user)
        async with client:
            response = await client.get(
                "/v1/benchmarks/cis/microsoft-365-foundations/v3.1.0/controls/CIS-1.1.1"
            )

    assert response.status_code == 200
    assert response.json()["title"] == "Ensure MFA"


@pytest.mark.asyncio
async def test_get_control_not_found(
    client_factory,
    viewer_user: User,
) -> None:
    reader = MagicMock()
    reader.get_control_metadata.side_effect = ValueError("missing control")

    with patch("app.api.v1.benchmarks.get_file_reader", return_value=reader):
        client: AsyncClient = client_factory(viewer_user)
        async with client:
            response = await client.get(
                "/v1/benchmarks/cis/microsoft-365-foundations/v3.1.0/controls/CIS-9.9.9"
            )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_list_benchmarks_unauthorized(client_factory) -> None:
    client: AsyncClient = client_factory(None)
    async with client:
        response = await client.get("/v1/benchmarks")

    assert response.status_code == 401
