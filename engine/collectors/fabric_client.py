"""Microsoft Fabric Admin API client.

The Fabric API is separate from the Microsoft Graph API and requires
different authentication scopes and base URL.

API Documentation: https://learn.microsoft.com/en-us/rest/api/fabric/admin
"""

from typing import Any

import httpx
from msal import ConfidentialClientApplication


class FabricClient:
    """Client for Microsoft Fabric Admin API."""

    FABRIC_BASE_URL = "https://api.fabric.microsoft.com/v1"
    FABRIC_SCOPE = "https://api.fabric.microsoft.com/.default"

    def __init__(self, tenant_id: str, client_id: str, client_secret: str):
        """Initialize the Fabric API client.

        Args:
            tenant_id: Azure AD tenant ID
            client_id: App registration client ID
            client_secret: App registration client secret
        """
        self.tenant_id = tenant_id
        self.client_id = client_id
        self.client_secret = client_secret
        self._access_token: str | None = None

        # Initialize MSAL client
        self._msal_app = ConfidentialClientApplication(
            client_id=client_id,
            client_credential=client_secret,
            authority=f"https://login.microsoftonline.com/{tenant_id}",
        )

    async def _get_access_token(self) -> str:
        """Get or refresh the Fabric API access token."""
        if self._access_token:
            return self._access_token

        # Acquire token for Fabric API
        result = self._msal_app.acquire_token_for_client(scopes=[self.FABRIC_SCOPE])

        if "access_token" not in result:
            error = result.get("error_description", result.get("error", "Unknown error"))
            raise Exception(f"Failed to acquire Fabric token: {error}")

        self._access_token = result["access_token"]
        return self._access_token

    async def _request(
        self,
        method: str,
        endpoint: str,
        params: dict | None = None,
        json_data: dict | None = None,
    ) -> dict[str, Any]:
        """Make a request to the Fabric Admin API.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path (e.g., /admin/tenantsettings)
            params: Query parameters
            json_data: JSON body for POST/PATCH requests

        Returns:
            Response JSON as dictionary
        """
        token = await self._get_access_token()

        async with httpx.AsyncClient() as client:
            response = await client.request(
                method=method,
                url=f"{self.FABRIC_BASE_URL}{endpoint}",
                headers={"Authorization": f"Bearer {token}"},
                params=params,
                json=json_data,
                timeout=60.0,
            )
            response.raise_for_status()
            return response.json() if response.content else {}

    async def get(
        self, endpoint: str, params: dict | None = None
    ) -> dict[str, Any]:
        """GET request to Fabric Admin API.

        Args:
            endpoint: API endpoint path
            params: Query parameters

        Returns:
            Response JSON
        """
        return await self._request("GET", endpoint, params=params)

    async def get_tenant_settings(self) -> list[dict[str, Any]]:
        """Get all Fabric tenant settings.

        Returns:
            List of tenant setting objects with structure:
            - settingName: Internal name of the setting
            - title: Display name
            - enabled: Whether the setting is enabled
            - tenantSettingGroup: Category grouping
            - canSpecifySecurityGroups: Whether security groups can be specified
            - enabledSecurityGroups: List of enabled security group IDs
        """
        response = await self.get("/admin/tenantsettings")
        return response.get("tenantSettings", [])
