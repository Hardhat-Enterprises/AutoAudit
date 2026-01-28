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
        # Get all users with relevant properties
        users = await client.get_all_pages(
            "/users",
            params={
                "$select": "id,userPrincipalName,displayName,accountEnabled,userType,onPremisesSyncEnabled,assignedLicenses"
            },
        )

        # Categorize users
        synced_users = [u for u in users if u.get("onPremisesSyncEnabled")]
        cloud_only_users = [u for u in users if not u.get("onPremisesSyncEnabled")]
        guest_users = [u for u in users if u.get("userType") == "Guest"]
        member_users = [u for u in users if u.get("userType") == "Member"]
        disabled_users = [u for u in users if not u.get("accountEnabled")]

        return {
            "users": users,
            "total_users": len(users),
            "synced_users_count": len(synced_users),
            "cloud_only_users_count": len(cloud_only_users),
            "guest_users_count": len(guest_users),
            "member_users_count": len(member_users),
            "disabled_users_count": len(disabled_users),
            "enabled_users_count": len(users) - len(disabled_users),
        }
