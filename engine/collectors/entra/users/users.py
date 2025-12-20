"""Users collector.

CIS Microsoft 365 Foundations Benchmark Controls:
    v6.0.0: 1.1.1, 1.1.4, 5.2.3.4

Connection Method: Microsoft Graph API
Required Scopes: User.Read.All
Graph Endpoint: /users
"""

from typing import Any

from collectors.base import BaseDataCollector
from collectors.graph_client import GraphClient


class UsersDataCollector(BaseDataCollector):
    """Collects user information for CIS compliance evaluation.

    This collector retrieves user properties including sync status,
    license assignments, and account types needed for compliance evaluation.
    """

    async def collect(self, client: GraphClient) -> dict[str, Any]:
        """Collect user data.

        Returns:
            Dict containing:
            - users: List of users with properties
            - total_users: Number of users
            - synced_users_count: Number of users synced from on-premises
            - cloud_only_users_count: Number of cloud-only users
        """
        # TODO: Implement collector
        raise NotImplementedError("Collector not yet implemented")
