"""SPO site collector.

CIS Microsoft 365 Foundations Benchmark Controls:
    v6.0.0: 7.2.4

Connection Method: Microsoft Graph
Authentication: Client secret via MSAL application permissions

Graph Endpoints: GET /sites/getAllSites
"""

from typing import Any

from collectors.base import BaseDataCollector
from collectors.sharepoint_client import SharePointClient


class SpoSiteDataCollector(BaseDataCollector):
    """Collects SPO site settings for CIS compliance evaluation.

    This collector retrieves OneDrive and SharePoint site-specific
    sharing settings for compliance evaluation.
    """

    @staticmethod
    def _first_present(data: dict[str, Any], *keys: str) -> Any:
        """Return the first non-missing value from a set of possible keys."""
        for key in keys:
            if key in data:
                return data[key]
        return None

    async def collect(self, client: SharePointClient) -> dict[str, Any]:
        """Collect SPO site data.

        Returns:
            Dict containing:
            - sites: List of site collections with settings
            - onedrive_sites: OneDrive for Business sites
            - site_sharing_settings: Per-site sharing configurations
        """
        tenant_settings = await client.get_tenant_settings()
        sites = await client.search_sites()

        onedrive_sites = [
            site for site in sites if "-my.sharepoint.com/" in str(site.get("url", ""))
        ]

        return {
            "sites": sites,
            "onedrive_sites": onedrive_sites,
            "site_sharing_settings": {
                "sharepoint_sharing_capability": self._first_present(
                    tenant_settings,
                    "sharingCapability",
                    "coreSharingCapability",
                    "SharingCapability",
                    "CoreSharingCapability",
                ),
                "onedrive_sharing_capability": self._first_present(
                    tenant_settings,
                    "oneDriveSharingCapability",
                    "OneDriveSharingCapability",
                ),
                "core_default_share_link_scope": self._first_present(
                    tenant_settings,
                    "coreDefaultShareLinkScope",
                    "CoreDefaultShareLinkScope",
                ),
                "onedrive_default_share_link_scope": self._first_present(
                    tenant_settings,
                    "oneDriveDefaultShareLinkScope",
                    "OneDriveDefaultShareLinkScope",
                ),
            },
        }
