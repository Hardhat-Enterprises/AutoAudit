"""HTTP-level tests for DVMClient.

The existing collector tests (test_patch_applications_collector.py) mock
get_software_inventory() directly, which never exercises DVMClient's own
URL construction, auth header, token scope, response parsing, or
pagination logic. These tests mock httpx.AsyncClient and MSAL directly
instead, so a real bug in DVMClient itself (wrong URL, wrong scope,
wrong header, broken pagination) would actually be caught here, rather
than silently passing because the collector tests never call into it.

Matches the existing repo convention: asyncio.run() inside plain sync
test functions, no pytest-asyncio.
"""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from collectors.dvm_client import DVMClient, DVMExecutionError


def _make_client() -> DVMClient:
    with patch("collectors.dvm_client.ConfidentialClientApplication"):
        return DVMClient(
            tenant_id="00000000-0000-0000-0000-000000000000",
            client_id="test-client-id",
            client_secret="test-client-secret",
        )


def _mock_token_success(client: DVMClient, token: str = "fake-token") -> None:
    client._msal_app.acquire_token_for_client = MagicMock(
        return_value={"access_token": token}
    )


def _mock_httpx_response(json_data: dict, status_code: int = 200) -> MagicMock:
    response = MagicMock(spec=httpx.Response)
    response.status_code = status_code
    response.json.return_value = json_data
    response.raise_for_status = MagicMock()
    if status_code >= 400:
        response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "error", request=MagicMock(), response=response
        )
    return response


# --- token acquisition ---


def test_get_token_uses_correct_scope():
    # Confirms the fix for the reviewer's finding: token audience must be
    # the legacy api.securitycenter.microsoft.com resource, not
    # api.security.microsoft.com, or real calls fail with 403.
    client = _make_client()
    _mock_token_success(client)

    client._get_token()

    client._msal_app.acquire_token_for_client.assert_called_once_with(
        scopes=["https://api.securitycenter.microsoft.com/.default"]
    )


def test_get_token_raises_on_missing_access_token():
    client = _make_client()
    client._msal_app.acquire_token_for_client = MagicMock(
        return_value={"error": "invalid_client", "error_description": "bad secret"}
    )

    with pytest.raises(DVMExecutionError, match="bad secret"):
        client._get_token()


# --- get() ---


def test_get_calls_correct_url_and_auth_header():
    client = _make_client()
    _mock_token_success(client, token="my-token")

    mock_response = _mock_httpx_response({"value": []})
    mock_http_client = AsyncMock()
    mock_http_client.get.return_value = mock_response
    mock_http_client.__aenter__.return_value = mock_http_client
    mock_http_client.__aexit__.return_value = None

    with patch("collectors.dvm_client.httpx.AsyncClient", return_value=mock_http_client):
        asyncio.run(client.get("/machines/SoftwareInventoryByMachine"))

    call_args = mock_http_client.get.call_args
    assert call_args.args[0] == (
        "https://api.security.microsoft.com/api/machines/SoftwareInventoryByMachine"
    )
    assert call_args.kwargs["headers"] == {"Authorization": "Bearer my-token"}


def test_get_raises_on_http_error():
    client = _make_client()
    _mock_token_success(client)

    mock_response = _mock_httpx_response({}, status_code=403)
    mock_http_client = AsyncMock()
    mock_http_client.get.return_value = mock_response
    mock_http_client.__aenter__.return_value = mock_http_client
    mock_http_client.__aexit__.return_value = None

    with patch("collectors.dvm_client.httpx.AsyncClient", return_value=mock_http_client):
        with pytest.raises(httpx.HTTPStatusError):
            asyncio.run(client.get("/machines/SoftwareInventoryByMachine"))


def test_get_returns_parsed_json():
    client = _make_client()
    _mock_token_success(client)

    mock_response = _mock_httpx_response({"value": [{"deviceId": "d1"}]})
    mock_http_client = AsyncMock()
    mock_http_client.get.return_value = mock_response
    mock_http_client.__aenter__.return_value = mock_http_client
    mock_http_client.__aexit__.return_value = None

    with patch("collectors.dvm_client.httpx.AsyncClient", return_value=mock_http_client):
        result = asyncio.run(client.get("/machines/SoftwareInventoryByMachine"))

    assert result == {"value": [{"deviceId": "d1"}]}


# --- get_all_pages() ---


def test_get_all_pages_single_page():
    client = _make_client()
    _mock_token_success(client)

    mock_response = _mock_httpx_response(
        {"value": [{"deviceId": "d1"}, {"deviceId": "d2"}]}
    )
    mock_http_client = AsyncMock()
    mock_http_client.get.return_value = mock_response
    mock_http_client.__aenter__.return_value = mock_http_client
    mock_http_client.__aexit__.return_value = None

    with patch("collectors.dvm_client.httpx.AsyncClient", return_value=mock_http_client):
        result = asyncio.run(client.get_all_pages("/machines/SoftwareInventoryByMachine"))

    assert result == [{"deviceId": "d1"}, {"deviceId": "d2"}]
    assert mock_http_client.get.call_count == 1


def test_get_all_pages_follows_next_link():
    client = _make_client()
    _mock_token_success(client)

    page1 = _mock_httpx_response(
        {
            "value": [{"deviceId": "d1"}],
            "@odata.nextLink": "https://api.security.microsoft.com/api/machines/SoftwareInventoryByMachine?page=2",
        }
    )
    page2 = _mock_httpx_response({"value": [{"deviceId": "d2"}]})

    mock_http_client = AsyncMock()
    mock_http_client.get.side_effect = [page1, page2]
    mock_http_client.__aenter__.return_value = mock_http_client
    mock_http_client.__aexit__.return_value = None

    with patch("collectors.dvm_client.httpx.AsyncClient", return_value=mock_http_client):
        result = asyncio.run(client.get_all_pages("/machines/SoftwareInventoryByMachine"))

    assert result == [{"deviceId": "d1"}, {"deviceId": "d2"}]
    assert mock_http_client.get.call_count == 2
    # Second call must use the full nextLink URL, not the original endpoint
    second_call_url = mock_http_client.get.call_args_list[1].args[0]
    assert second_call_url == (
        "https://api.security.microsoft.com/api/machines/SoftwareInventoryByMachine?page=2"
    )


def test_get_all_pages_stops_without_next_link():
    client = _make_client()
    _mock_token_success(client)

    mock_response = _mock_httpx_response({"value": [{"deviceId": "d1"}]})
    mock_http_client = AsyncMock()
    mock_http_client.get.return_value = mock_response
    mock_http_client.__aenter__.return_value = mock_http_client
    mock_http_client.__aexit__.return_value = None

    with patch("collectors.dvm_client.httpx.AsyncClient", return_value=mock_http_client):
        asyncio.run(client.get_all_pages("/machines/SoftwareInventoryByMachine"))

    assert mock_http_client.get.call_count == 1


def test_get_all_pages_empty_response():
    client = _make_client()
    _mock_token_success(client)

    mock_response = _mock_httpx_response({"value": []})
    mock_http_client = AsyncMock()
    mock_http_client.get.return_value = mock_response
    mock_http_client.__aenter__.return_value = mock_http_client
    mock_http_client.__aexit__.return_value = None

    with patch("collectors.dvm_client.httpx.AsyncClient", return_value=mock_http_client):
        result = asyncio.run(client.get_all_pages("/machines/SoftwareInventoryByMachine"))

    assert result == []


def test_get_all_pages_missing_value_key_does_not_crash():
    # A malformed or unexpected response shape (no "value" key) should
    # not crash the collector; get_all_pages defaults to an empty list
    # for that page rather than raising a KeyError.
    client = _make_client()
    _mock_token_success(client)

    mock_response = _mock_httpx_response({})
    mock_http_client = AsyncMock()
    mock_http_client.get.return_value = mock_response
    mock_http_client.__aenter__.return_value = mock_http_client
    mock_http_client.__aexit__.return_value = None

    with patch("collectors.dvm_client.httpx.AsyncClient", return_value=mock_http_client):
        result = asyncio.run(client.get_all_pages("/machines/SoftwareInventoryByMachine"))

    assert result == []


# --- get_software_inventory() ---


def test_get_software_inventory_calls_correct_endpoint():
    client = _make_client()
    _mock_token_success(client)

    mock_response = _mock_httpx_response({"value": [{"deviceId": "d1", "softwareName": "Google Chrome"}]})
    mock_http_client = AsyncMock()
    mock_http_client.get.return_value = mock_response
    mock_http_client.__aenter__.return_value = mock_http_client
    mock_http_client.__aexit__.return_value = None

    with patch("collectors.dvm_client.httpx.AsyncClient", return_value=mock_http_client):
        result = asyncio.run(client.get_software_inventory())

    called_url = mock_http_client.get.call_args.args[0]
    assert called_url == (
        "https://api.security.microsoft.com/api/machines/SoftwareInventoryByMachine"
    )
    assert result == [{"deviceId": "d1", "softwareName": "Google Chrome"}]
