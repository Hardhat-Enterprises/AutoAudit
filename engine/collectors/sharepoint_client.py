"""SharePoint REST API client.

This module provides connectivity to SharePoint Online using REST API instead
of PowerShell because SharePoint Online PowerShell does not support client
secret authentication for app-only scenarios.

Authentication: Client secret via MSAL -> access token for SharePoint resource

NOTE: If certificate authentication is adopted in the future, consider replacing
these REST API calls with PowerShell cmdlets (Get-SPOTenant, Get-SPOSite, etc.)
for consistency with other collectors.

SharePoint REST API Reference:
- Tenant Admin API: https://{tenant}-admin.sharepoint.com/_api/
- Site API: https://{site-url}/_api/
"""

from typing import Any

import httpx
from msal import ConfidentialClientApplication


class SharePointClient:
    """Client for SharePoint Online REST API using client secret auth."""

    def __init__(self, tenant_id: str, client_id: str, client_secret: str, tenant_name: str):
        """Initialize SharePoint client.

        Args:
            tenant_id: Azure AD tenant ID
            client_id: Application (client) ID
            client_secret: Client secret for authentication
            tenant_name: SharePoint tenant name (e.g., 'contoso' for contoso.sharepoint.com)
        """
        self.tenant_id = tenant_id
        self.client_id = client_id
        self.client_secret = client_secret
        self.tenant_name = tenant_name
        self.admin_url = f"https://{tenant_name}-admin.sharepoint.com"
        self._access_token: str | None = None

        self._msal_app = ConfidentialClientApplication(
            client_id=client_id,
            client_credential=client_secret,
            authority=f"https://login.microsoftonline.com/{tenant_id}",
        )

    async def _get_access_token(self) -> str:
        """Get access token for SharePoint.

        Returns:
            Access token string.

        Raises:
            Exception: If token acquisition fails.
        """
        if self._access_token:
            return self._access_token

        result = self._msal_app.acquire_token_for_client(
            scopes=[f"{self.admin_url}/.default"]
        )
        if "access_token" not in result:
            error = result.get("error_description", result.get("error", "Unknown"))
            raise Exception(f"Failed to acquire SharePoint token: {error}")

        self._access_token = result["access_token"]
        return self._access_token

    async def get_tenant_settings(self) -> dict[str, Any]:
        """Get SPO tenant settings via REST API.

        Returns:
            Dict containing tenant configuration properties.
        """
        # TODO: Implement REST API call
        raise NotImplementedError("SharePoint client not yet implemented")

    async def get_site_properties(self, site_url: str) -> dict[str, Any]:
        """Get site properties via REST API.

        Args:
            site_url: The SharePoint site URL

        Returns:
            Dict containing site properties.
        """
        # TODO: Implement REST API call
        raise NotImplementedError("SharePoint client not yet implemented")

    async def get_sync_client_restriction(self) -> dict[str, Any]:
        """Get OneDrive sync client restriction settings.

        Returns:
            Dict containing sync client restriction settings.
        """
        # TODO: Implement REST API call
        raise NotImplementedError("SharePoint client not yet implemented")
