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
                "sharepoint_sharing_capability": tenant_settings.get(
                    "CoreSharingCapability",
                    tenant_settings.get("SharingCapability"),
                ),
                "onedrive_sharing_capability": tenant_settings.get(
                    "OneDriveSharingCapability"
                ),
                "core_default_share_link_scope": tenant_settings.get(
                    "CoreDefaultShareLinkScope"
                ),
                "onedrive_default_share_link_scope": tenant_settings.get(
                    "OneDriveDefaultShareLinkScope"
                ),
            },
        }
