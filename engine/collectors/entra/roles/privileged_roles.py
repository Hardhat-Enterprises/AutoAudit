"""Privileged roles data collector.

CIS-1.1.3: Ensure that between two and four global admins are designated.
Maintain 2-4 global administrators for operational continuity and security.
"""

from typing import Any

from collectors.base import BaseDataCollector
from collectors.graph_client import GraphClient


class PrivilegedRolesDataCollector(BaseDataCollector):
    """Collects global admin count and members."""

    GLOBAL_ADMIN_ROLE_NAME = "Global Administrator"

    async def collect(self, client: GraphClient) -> dict[str, Any]:
        """Collect global admin information.

        Returns:
            Dict with:
            - global_admin_count: Number of global admins
            - global_admins: List of UPNs
            - global_admin_details: List of admin details (id, UPN, displayName)
        """
        # Get all directory roles
        roles = await client.get_directory_roles()

        # Find Global Administrator role
        global_admin_role = None
        for role in roles:
            if role.get("displayName") == self.GLOBAL_ADMIN_ROLE_NAME:
                global_admin_role = role
                break

        if not global_admin_role:
            return {
                "global_admin_count": 0,
                "global_admins": [],
                "global_admin_details": [],
                "error": "Global Administrator role not found",
            }

        # Get members of the Global Administrator role
        members = await client.get_role_members(global_admin_role["id"])

        global_admins = [
            {
                "id": m.get("id"),
                "userPrincipalName": m.get("userPrincipalName"),
                "displayName": m.get("displayName"),
            }
            for m in members
            if m.get("@odata.type") == "#microsoft.graph.user"
        ]

        return {
            "global_admin_count": len(global_admins),
            "global_admins": [ga["userPrincipalName"] for ga in global_admins],
            "global_admin_details": global_admins,
        }
