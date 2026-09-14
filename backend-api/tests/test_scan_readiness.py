"""Unit tests for scan readiness helpers."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.services.m365_graph import M365ConnectionError
from app.services.scan_readiness import (
    evaluate_scan_readiness,
    extract_graph_error_detail,
    extract_required_permissions,
)


def test_extract_required_permissions() -> None:
    controls = [
        {
            "automation_status": "ready",
            "requires_permissions": ["User.Read.All", " User.Read.All "],
        },
        {"automation_status": "manual", "requires_permissions": ["Policy.Read.All"]},
        {
            "automation_status": "ready",
            "requires_permissions": [None, "Group.Read.All"],
        },
    ]
    assert extract_required_permissions(controls) == [
        "Group.Read.All",
        "User.Read.All",
    ]


def test_extract_graph_error_detail() -> None:
    resp = MagicMock()
    resp.json.return_value = {"error": {"message": " denied "}}
    resp.text = ""
    assert extract_graph_error_detail(resp) == "denied"

    resp.json.return_value = {"detail": " plain "}
    assert extract_graph_error_detail(resp) == "plain"

    resp.json.side_effect = ValueError("bad json")
    resp.text = "raw\nline"
    assert extract_graph_error_detail(resp) == "raw"

    resp.text = ""
    assert extract_graph_error_detail(resp) is None


@pytest.mark.asyncio
async def test_evaluate_scan_readiness_auth_failure() -> None:
    with patch(
        "app.services.scan_readiness.validate_m365_connection",
        new=AsyncMock(side_effect=M365ConnectionError("bad creds")),
    ):
        result = await evaluate_scan_readiness(
            tenant_id="t",
            client_id="c",
            client_secret="s",
            required_permissions=["User.Read.All"],
        )
    assert result.ready is False
    assert result.checks[0].status == "fail"


@pytest.mark.asyncio
async def test_evaluate_scan_readiness_ready_with_mixed_probes() -> None:
    async def fake_get(path, headers=None):
        resp = MagicMock()
        if "organization" in path:
            resp.status_code = 200
        elif "users" in path:
            resp.status_code = 403
        elif "directoryRoles" in path:
            resp.status_code = 500
            resp.json.return_value = {"error": {"message": "timeout"}}
            resp.text = "timeout"
        else:
            resp.status_code = 200
        return resp

    with patch(
        "app.services.scan_readiness.validate_m365_connection",
        new=AsyncMock(return_value=None),
    ), patch(
        "app.services.scan_readiness.acquire_graph_access_token",
        new=AsyncMock(return_value="tok"),
    ), patch(
        "app.services.scan_readiness.httpx.AsyncClient"
    ) as client_cls:
        client = AsyncMock()
        client.__aenter__.return_value = client
        client.__aexit__.return_value = None
        client.get = AsyncMock(side_effect=fake_get)
        client_cls.return_value = client

        result = await evaluate_scan_readiness(
            tenant_id="t",
            client_id="c",
            client_secret="s",
            required_permissions=["User.Read.All", "Custom.Unknown"],
        )

    assert result.ready is False  # critical baseline User.Read.All denied
    assert "User.Read.All" in result.missing_permissions
    assert "Custom.Unknown" in result.unverified_permissions
