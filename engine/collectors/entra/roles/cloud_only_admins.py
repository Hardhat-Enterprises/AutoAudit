"""Cloud-only admins data collector.

CIS-1.1.1: Ensure Administrative accounts are cloud-only.
Administrative accounts should not be synced from on-premises Active Directory.
"""

from typing import Any

from collectors.base import BaseDataCollector
from collectors.graph_client import GraphClient


class CloudOnlyAdminsDataCollector(BaseDataCollector):
    """Collects admin accounts and checks if they are cloud-only."""

    # Roles that are considered administrative
    ADMIN_ROLE_NAMES = [
        "Global Administrator",
        "Privileged Role Administrator",
        "Privileged Authentication Administrator",
        "Security Administrator",
        "Exchange Administrator",
        "SharePoint Administrator",
        "Intune Administrator",
        "Application Administrator",
        "Cloud Application Administrator",
        "Azure AD Joined Device Local Administrator",
        "Compliance Administrator",
        "Conditional Access Administrator",
        "User Administrator",
    ]

    async def collect(self, client: GraphClient) -> dict[str, Any]:
        """Collect admin account information and check for on-prem sync.

        Returns:
            Dict with admin_accounts list, each containing:
            - userPrincipalName
            - displayName
            - on_premises_sync_enabled
            - admin_roles (list of roles the user holds)
        """
        # Get all directory roles
        roles = await client.get_directory_roles()

        # Find admin roles by name
        admin_roles = [
            role for role in roles if role.get("displayName") in self.ADMIN_ROLE_NAMES
        ]

        # Collect all admin users (deduplicated)
        admin_users: dict[str, dict[str, Any]] = {}

        for role in admin_roles:
            role_name = role.get("displayName", "Unknown")
            members = await client.get_role_members(role["id"])

            for member in members:
                # Only process user objects
                if member.get("@odata.type") != "#microsoft.graph.user":
                    continue

                user_id = member.get("id")
                if not user_id:
                    continue

                if user_id in admin_users:
                    # Add role to existing user
                    admin_users[user_id]["admin_roles"].append(role_name)
                else:
                    # Get full user details including onPremisesSyncEnabled
                    user_details = await client.get(
                        f"/users/{user_id}",
                        params={
                            "$select": "id,userPrincipalName,displayName,onPremisesSyncEnabled"
                        },
                    )

                    admin_users[user_id] = {
                        "id": user_id,
                        "userPrincipalName": user_details.get("userPrincipalName"),
                        "displayName": user_details.get("displayName"),
                        "on_premises_sync_enabled": user_details.get(
                            "onPremisesSyncEnabled", False
                        )
                        or False,
                        "admin_roles": [role_name],
                    }

        admin_accounts = list(admin_users.values())

        return {
            "admin_accounts": admin_accounts,
            "total_admin_accounts": len(admin_accounts),
            "synced_admin_count": sum(
                1 for a in admin_accounts if a["on_premises_sync_enabled"]
            ),
            "cloud_only_admin_count": sum(
                1 for a in admin_accounts if not a["on_premises_sync_enabled"]
            ),
        }
