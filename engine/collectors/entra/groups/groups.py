"""Groups collector.

CIS Microsoft 365 Foundations Benchmark Controls:
    v6.0.0: 1.2.1, 5.1.3.1, 5.1.3.2

Connection Method: Microsoft Graph API
Required Scopes: Group.Read.All
Graph Endpoint: /groups
"""

from typing import Any

from collectors.base import BaseDataCollector
from collectors.graph_client import GraphClient


class GroupsDataCollector(BaseDataCollector):
    """Collects group information for CIS compliance evaluation.

    This collector retrieves group details including dynamic groups,
    public groups, and group settings needed for compliance evaluation.
    """

    async def collect(self, client: GraphClient) -> dict[str, Any]:
        """Collect group data.

        Returns:
            Dict containing:
            - groups: List of groups with properties
            - total_groups: Number of groups
            - dynamic_groups_count: Number of dynamic membership groups
            - public_groups_count: Number of public groups
        """
        # TODO: Implement collector
        raise NotImplementedError("Collector not yet implemented")
