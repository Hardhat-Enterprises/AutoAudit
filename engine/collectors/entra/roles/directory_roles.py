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
        # Get all directory roles
        roles = await client.get_directory_roles()

        # For each role, get members
        roles_with_members = []
        admin_users: dict[str, dict] = {}

        for role in roles:
            role_id = role.get("id")
            role_name = role.get("displayName", "")

            # Get members of this role
            members = await client.get_role_members(role_id)

            role_data = {
                "id": role_id,
                "displayName": role_name,
                "description": role.get("description"),
                "roleTemplateId": role.get("roleTemplateId"),
                "members": members,
                "members_count": len(members),
            }
            roles_with_members.append(role_data)

            # Collect unique admin users
            for member in members:
                if member.get("@odata.type") == "#microsoft.graph.user":
                    user_id = member.get("id")
                    if user_id not in admin_users:
                        admin_users[user_id] = {
                            "id": user_id,
                            "displayName": member.get("displayName"),
                            "userPrincipalName": member.get("userPrincipalName"),
                            "roles": [role_name],
                        }
                    else:
                        admin_users[user_id]["roles"].append(role_name)

        return {
            "directory_roles": roles_with_members,
            "total_roles": len(roles_with_members),
            "admin_users": list(admin_users.values()),
            "admin_users_count": len(admin_users),
        }
