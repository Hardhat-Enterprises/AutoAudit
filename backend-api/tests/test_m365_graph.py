"""Unit tests for M365 Graph helpers (no live Graph calls)."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.services.m365_graph import (
    M365ConnectionError,
    TenantDetails,
    _first_line,
    acquire_graph_access_token,
    probe_tenant_details,
    validate_m365_connection,
)


def test_first_line_helpers() -> None:
    assert _first_line(None) == "Unknown error"
    assert _first_line("") == "Unknown error"
    assert _first_line("line1\nline2") == "line1"


@pytest.mark.asyncio
async def test_acquire_graph_access_token_missing_fields() -> None:
    with pytest.raises(M365ConnectionError, match="Missing"):
        await acquire_graph_access_token(tenant_id="", client_id="c", client_secret="s")


@pytest.mark.asyncio
async def test_acquire_graph_access_token_success_and_errors() -> None:
    with patch(
        "app.services.m365_graph.anyio.to_thread.run_sync",
        new=AsyncMock(return_value={"access_token": "tok"}),
    ):
        token = await acquire_graph_access_token(
            tenant_id="t", client_id="c", client_secret="s"
        )
    assert token == "tok"

    with patch(
        "app.services.m365_graph.anyio.to_thread.run_sync",
        new=AsyncMock(return_value={"error_description": "bad secret\nmore"}),
    ):
        with pytest.raises(M365ConnectionError, match="Authentication failed"):
            await acquire_graph_access_token(
                tenant_id="t", client_id="c", client_secret="s"
            )

    with patch(
        "app.services.m365_graph.anyio.to_thread.run_sync",
        new=AsyncMock(side_effect=ValueError("bad tenant")),
    ):
        with pytest.raises(M365ConnectionError, match="Authentication failed"):
            await acquire_graph_access_token(
                tenant_id="t", client_id="c", client_secret="s"
            )


@pytest.mark.asyncio
async def test_probe_tenant_details_paths() -> None:
    forbidden = MagicMock()
    forbidden.status_code = 403
    with patch("app.services.m365_graph.httpx.AsyncClient") as client_cls:
        client = AsyncMock()
        client.__aenter__.return_value = client
        client.__aexit__.return_value = None
        client.get = AsyncMock(return_value=forbidden)
        client_cls.return_value = client
        with pytest.raises(M365ConnectionError, match="Organization.Read.All"):
            await probe_tenant_details(access_token="tok")

    error_resp = MagicMock()
    error_resp.status_code = 500
    error_resp.json.return_value = {"error": {"message": "boom\nextra"}}
    error_resp.text = "boom"
    with patch("app.services.m365_graph.httpx.AsyncClient") as client_cls:
        client = AsyncMock()
        client.__aenter__.return_value = client
        client.__aexit__.return_value = None
        client.get = AsyncMock(return_value=error_resp)
        client_cls.return_value = client
        with pytest.raises(M365ConnectionError, match="Graph probe failed"):
            await probe_tenant_details(access_token="tok")

    empty = MagicMock()
    empty.status_code = 200
    empty.json.return_value = {"value": []}
    with patch("app.services.m365_graph.httpx.AsyncClient") as client_cls:
        client = AsyncMock()
        client.__aenter__.return_value = client
        client.__aexit__.return_value = None
        client.get = AsyncMock(return_value=empty)
        client_cls.return_value = client
        details = await probe_tenant_details(access_token="tok")
    assert details.verified_domains == []

    ok = MagicMock()
    ok.status_code = 200
    ok.json.return_value = {
        "value": [
            {
                "displayName": "Contoso",
                "verifiedDomains": [
                    {"name": "contoso.com", "isDefault": True},
                    {"name": "contoso.onmicrosoft.com", "isDefault": False},
                ],
            }
        ]
    }
    with patch("app.services.m365_graph.httpx.AsyncClient") as client_cls:
        client = AsyncMock()
        client.__aenter__.return_value = client
        client.__aexit__.return_value = None
        client.get = AsyncMock(return_value=ok)
        client_cls.return_value = client
        details = await probe_tenant_details(access_token="tok")
    assert details.tenant_display_name == "Contoso"
    assert details.default_domain == "contoso.com"
    assert details.verified_domains == [
        "contoso.com",
        "contoso.onmicrosoft.com",
    ]


@pytest.mark.asyncio
async def test_validate_m365_connection_wires_helpers() -> None:
    expected = TenantDetails(
        tenant_display_name="Contoso",
        default_domain="contoso.com",
        verified_domains=["contoso.com"],
    )
    with patch(
        "app.services.m365_graph.acquire_graph_access_token",
        new=AsyncMock(return_value="tok"),
    ), patch(
        "app.services.m365_graph.probe_tenant_details",
        new=AsyncMock(return_value=expected),
    ):
        details = await validate_m365_connection(
            tenant_id="t", client_id="c", client_secret="s"
        )
    assert details is expected
