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
        # TODO: Implement collector
        raise NotImplementedError("Collector not yet implemented")
