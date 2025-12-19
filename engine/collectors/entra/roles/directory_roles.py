"""Directory roles collector.

CIS Microsoft 365 Foundations Benchmark Controls:
    v6.0.0: 1.1.1, 1.1.3, 1.1.4

Connection Method: Microsoft Graph API
Required Scopes: RoleManagement.Read.Directory, User.Read.All
Graph Endpoint: /directoryRoles, /directoryRoles/{id}/members, /users/{id}
"""

from typing import Any

from collectors.base import BaseDataCollector
from collectors.graph_client import GraphClient


class DirectoryRolesDataCollector(BaseDataCollector):
    """Collects directory role assignments for CIS compliance evaluation.

    This collector retrieves all directory roles and their members, including
    user properties needed to evaluate administrative account compliance.
    """

    async def collect(self, client: GraphClient) -> dict[str, Any]:
        """Collect directory roles and member information.

        Returns:
            Dict containing:
            - directory_roles: List of roles with their members
            - total_roles: Number of directory roles
            - admin_users: Deduplicated list of users with admin roles
        """
        # TODO: Implement collector
        raise NotImplementedError("Collector not yet implemented")
