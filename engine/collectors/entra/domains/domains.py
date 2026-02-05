"""Domains collector.

CIS Microsoft 365 Foundations Benchmark Controls:
    v6.0.0: 1.3.1

Connection Method: Microsoft Graph API
Required Scopes: Domain.Read.All
Graph Endpoint: /domains
"""

from typing import Any

from collectors.base import BaseDataCollector
from collectors.graph_client import GraphClient


class DomainsDataCollector(BaseDataCollector):
    """Collects domain configuration for CIS compliance evaluation.

    This collector retrieves domain settings including password validity
    period configuration needed for password expiration policy compliance.
    """

    async def collect(self, client: GraphClient) -> dict[str, Any]:
        """Collect domain configuration data.

        Returns:
            Dict containing:
            - domains: List of domains with configuration details
            - total_domains: Number of domains
            - managed_domains_count: Number of managed (non-federated) domains
        """
        # Get all domains
        domains = await client.get_domains()

        # Categorize domains
        verified_domains = [d for d in domains if d.get("isVerified")]
        managed_domains = [d for d in domains if d.get("authenticationType") == "Managed"]
        federated_domains = [d for d in domains if d.get("authenticationType") == "Federated"]

        return {
            "domains": domains,
            "total_domains": len(domains),
            "verified_domains_count": len(verified_domains),
            "managed_domains_count": len(managed_domains),
            "federated_domains_count": len(federated_domains),
            "default_domain": next(
                (d for d in domains if d.get("isDefault")), None
            ),
            "initial_domain": next(
                (d for d in domains if d.get("isInitial")), None
            ),
        }
