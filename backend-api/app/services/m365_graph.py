"""Microsoft 365 (Graph) connection helpers.

This module validates app-only (client credentials) connectivity to a target tenant
and probes basic tenant details via Microsoft Graph.

We intentionally keep error messages user-safe so API layers can surface them
directly in HTTP responses without leaking secrets.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import partial

import anyio
import httpx
from msal import ConfidentialClientApplication

GRAPH_SCOPES = ["https://graph.microsoft.com/.default"]
GRAPH_ORG_ENDPOINT = "/v1.0/organization?$select=id,displayName,verifiedDomains"


@dataclass(frozen=True)
class TenantDetails:
    """Normalized tenant details returned from Graph."""

    tenant_display_name: str | None
    default_domain: str | None
    verified_domains: list[str]


class M365ConnectionError(Exception):
    """Raised when M365 auth/probe fails in a user-displayable way."""


def _first_line(value: str | None) -> str:
    if not value:
        return "Unknown error"
    return value.splitlines()[0].strip() or "Unknown error"


def _acquire_token_sync(*, tenant_id: str, client_id: str, client_secret: str) -> dict:
    """Acquire an app-only token for Microsoft Graph (sync; run in thread)."""
    app = ConfidentialClientApplication(
        client_id=client_id,
        client_credential=client_secret,
        authority=f"https://login.microsoftonline.com/{tenant_id}",
    )
    return app.acquire_token_for_client(scopes=GRAPH_SCOPES)


async def acquire_graph_access_token(
    *, tenant_id: str, client_id: str, client_secret: str
) -> str:
    """Acquire an app-only access token for Microsoft Graph."""
    tenant_id = (tenant_id or "").strip()
    client_id = (client_id or "").strip()
    client_secret = (client_secret or "").strip()

    if not tenant_id or not client_id or not client_secret:
        raise M365ConnectionError("Missing tenant_id, client_id, or client_secret")

    try:
        result = await anyio.to_thread.run_sync(
            partial(
                _acquire_token_sync,
                tenant_id=tenant_id,
                client_id=client_id,
                client_secret=client_secret,
            )
        )
    except Exception as e:
        # MSAL can raise (e.g.) ValueError for invalid tenant/authority formats.
        raise M365ConnectionError(f"Authentication failed: {_first_line(str(e))}")

    token = result.get("access_token")
    if token:
        return token

    # Typical errors include AADSTS codes like:
    # - AADSTS90002 (tenant not found)
    # - AADSTS700016 (app not found)
    # - AADSTS7000215 (invalid secret)
    desc = _first_line(result.get("error_description") or result.get("error"))
    raise M365ConnectionError(f"Authentication failed: {desc}")


async def probe_tenant_details(*, access_token: str) -> TenantDetails:
    """Probe basic tenant details via Graph /organization."""
    base_url = "https://graph.microsoft.com"
    headers = {"Authorization": f"Bearer {access_token}"}

    async with httpx.AsyncClient(timeout=15.0, base_url=base_url) as http:
        resp = await http.get(GRAPH_ORG_ENDPOINT, headers=headers)

    if resp.status_code == 403:
        raise M365ConnectionError(
            "Authenticated, but Graph denied access to /organization. "
            "Add Microsoft Graph Application permission 'Organization.Read.All' and grant admin consent."
        )

    if resp.status_code >= 400:
        try:
            payload = resp.json()
            # Graph error shape: {"error": {"code": "...", "message": "..."}}
            if isinstance(payload.get("error"), dict):
                msg = payload["error"].get("message")
            else:
                msg = str(payload.get("error") or "")
        except Exception:
            msg = resp.text
        raise M365ConnectionError(f"Graph probe failed: {_first_line(msg)}")

    data = resp.json()
    orgs = data.get("value") or []
    if not orgs:
        return TenantDetails(
            tenant_display_name=None,
            default_domain=None,
            verified_domains=[],
        )

    org = orgs[0] or {}
    display_name = org.get("displayName")

    verified = org.get("verifiedDomains") or []
    verified_domains = [d.get("name") for d in verified if isinstance(d, dict) and d.get("name")]
    default_domain = next(
        (
            d.get("name")
            for d in verified
            if isinstance(d, dict) and d.get("isDefault") and d.get("name")
        ),
        None,
    )

    return TenantDetails(
        tenant_display_name=display_name,
        default_domain=default_domain,
        verified_domains=verified_domains,
    )


async def validate_m365_connection(
    *, tenant_id: str, client_id: str, client_secret: str
) -> TenantDetails:
    """Validate credentials by acquiring a token and probing tenant details."""
    token = await acquire_graph_access_token(
        tenant_id=tenant_id,
        client_id=client_id,
        client_secret=client_secret,
    )
    return await probe_tenant_details(access_token=token)


