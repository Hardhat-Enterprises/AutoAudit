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
        # Get all groups with relevant properties
        groups = await client.get_all_pages(
            "/groups",
            params={
                "$select": "id,displayName,groupTypes,membershipRule,visibility,securityEnabled,mailEnabled"
            },
        )

        # Categorize groups
        dynamic_groups = [
            g for g in groups
            if "DynamicMembership" in g.get("groupTypes", [])
        ]
        public_groups = [
            g for g in groups
            if g.get("visibility") == "Public"
        ]
        security_groups = [
            g for g in groups
            if g.get("securityEnabled")
        ]
        m365_groups = [
            g for g in groups
            if "Unified" in g.get("groupTypes", [])
        ]

        return {
            "groups": groups,
            "total_groups": len(groups),
            "dynamic_groups": dynamic_groups,
            "dynamic_groups_count": len(dynamic_groups),
            "public_groups": public_groups,
            "public_groups_count": len(public_groups),
            "security_groups_count": len(security_groups),
            "m365_groups_count": len(m365_groups),
        }
