"""Service principals collector.

CIS Microsoft 365 Foundations Benchmark Controls:
    v6.0.0: 1.3.7

Connection Method: Microsoft Graph API
Required Scopes: Application.Read.All
Graph Endpoint: /servicePrincipals
"""

from typing import Any

from collectors.base import BaseDataCollector
from collectors.graph_client import GraphClient


class ServicePrincipalsDataCollector(BaseDataCollector):
    """Collects service principal information for CIS compliance evaluation.

    This collector retrieves service principal details to verify
    third-party storage service principal status and app configurations.
    """

    async def collect(self, client: GraphClient) -> dict[str, Any]:
        """Collect service principals data.

        Returns:
            Dict containing:
            - service_principals: List of service principals
            - total_service_principals: Number of service principals
            - third_party_storage_apps: Third-party storage service principals
        """
        # Get all service principals
        service_principals = await client.get_all_pages("/servicePrincipals")

        # Known third-party storage app IDs (Dropbox, Google Drive, Box, etc.)
        third_party_storage_app_names = [
            "dropbox",
            "google drive",
            "box",
            "egnyte",
            "citrix sharefile",
        ]

        # Filter for third-party storage apps
        third_party_storage_apps = [
            sp
            for sp in service_principals
            if any(
                name in (sp.get("displayName") or "").lower()
                for name in third_party_storage_app_names
            )
        ]

        return {
            "service_principals": service_principals,
            "total_service_principals": len(service_principals),
            "third_party_storage_apps": third_party_storage_apps,
            "third_party_storage_apps_count": len(third_party_storage_apps),
            "has_third_party_storage_apps": len(third_party_storage_apps) > 0,
        }
