"""Client for Microsoft Defender Vulnerability Management (DVM) API.

DVM sits on a separate API, api.security.microsoft.com, not Microsoft
Graph, and requires its own Entra app registration and permission,
distinct from the app registration AutoAudit's existing Graph and
PowerShell collectors use.

** PERMISSION NAME CONFIRMED **
This client requests the "Vulnerability.Read.All" application permission,
under the WindowsDefenderATP API. Confirmed against Microsoft's own
documentation (Get all vulnerabilities - Microsoft Defender for
Endpoint, learn.microsoft.com), not from the E8-PA-1.1 report, which
did not specify a permission name. Register the app permission via
Entra: API permissions > Add permission > APIs my organization uses >
WindowsDefenderATP > Application permissions > Vulnerability.Read.All.
This has NOT yet been tested against the live t8sjf tenant.
See app registration 7fdf4478-709b-4729-9e0d-e51ca822f465.
"""

from typing import Any

import httpx
from msal import ConfidentialClientApplication

from worker.validators import validate_tenant_id


class DVMExecutionError(Exception):
    """Raised when a DVM API call fails."""


class DVMClient:
    """Client for calling the Defender Vulnerability Management API."""

    DVM_BASE_URL = "https://api.security.microsoft.com/api"

    # UNVERIFIED: exact scope string not confirmed against a live tenant.
    DVM_SCOPE = "https://api.security.microsoft.com/.default"

    def __init__(self, tenant_id: str, client_id: str, client_secret: str):
        """Initialize the DVM client.

        Args:
            tenant_id: Azure AD tenant ID
            client_id: Application (client) ID of the DVM-permissioned
                app registration (NOT necessarily the same app registration
                used by GraphClient/PowerShellClient)
            client_secret: Client secret for authentication
        """
        self.tenant_id = validate_tenant_id(tenant_id)
        self.client_id = client_id
        self.client_secret = client_secret
        self._msal_app = ConfidentialClientApplication(
            client_id=client_id,
            client_credential=client_secret,
            authority=f"https://login.microsoftonline.com/{self.tenant_id}",
        )

    def _get_token(self) -> str:
        result = self._msal_app.acquire_token_for_client(scopes=[self.DVM_SCOPE])
        if "access_token" not in result:
            error_desc = result.get("error_description", str(result))
            raise DVMExecutionError(f"DVM token acquisition failed: {error_desc}")
        return result["access_token"]

    async def get(self, endpoint: str, params: dict | None = None) -> dict[str, Any]:
        """Make a GET request to the DVM API.

        Args:
            endpoint: API path, e.g. "/machines/software"
            params: Optional query parameters (e.g. OData $filter)

        Returns:
            Parsed JSON response.
        """
        token = self._get_token()
        url = f"{self.DVM_BASE_URL}{endpoint}"

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.get(
                url,
                headers={"Authorization": f"Bearer {token}"},
                params=params,
            )
            response.raise_for_status()

        return response.json()

    async def get_all_pages(
        self, endpoint: str, params: dict | None = None, max_pages: int = 100
    ) -> list[dict[str, Any]]:
        """Get all pages of a paginated DVM endpoint.

        DVM uses the same @odata.nextLink pagination pattern as Graph.
        """
        all_items: list[dict[str, Any]] = []
        current_url = f"{self.DVM_BASE_URL}{endpoint}"
        current_params = params
        token = self._get_token()

        async with httpx.AsyncClient(timeout=60.0) as client:
            for _ in range(max_pages):
                response = await client.get(
                    current_url,
                    headers={"Authorization": f"Bearer {token}"},
                    params=current_params,
                )
                response.raise_for_status()
                data = response.json()
                items = data.get("value", [])
                all_items.extend(items)

                next_link = data.get("@odata.nextLink")
                if not next_link:
                    break
                current_url = next_link
                current_params = None

        return all_items

    async def get_software_inventory(self) -> list[dict[str, Any]]:
        """Get per-device software inventory from DVM.

        UNVERIFIED: exact endpoint path not confirmed against a live
        tenant. Based on report 26T2-SEC-EG-003 reference 5:
        https://learn.microsoft.com/en-us/defender-vulnerability-management/tvm-software-inventory
        """
        return await self.get_all_pages("/machines/software")
