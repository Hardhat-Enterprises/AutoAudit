"""Legacy authentication block collector.

CIS Microsoft 365 Foundations Benchmark Controls:
    v6.0.0: 5.2.2.3

Connection Method: Microsoft Graph API
Required Scopes: Policy.Read.All
Graph Endpoint: /identity/conditionalAccess/policies
"""

from typing import Any

from collectors.base import BaseDataCollector
from collectors.graph_client import GraphClient


class LegacyAuthBlockDataCollector(BaseDataCollector):
    """Collects Conditional Access policies that block legacy authentication."""

    LEGACY_CLIENT_TYPES = {"exchangeActiveSync", "other"}

    async def collect(self, client: GraphClient) -> dict[str, Any]:
        """Collect Conditional Access policies and check for legacy auth blocking.

        Returns:
            Dict with conditional_access_policies list.
        """
        policies = await client.get_conditional_access_policies()

        policy_data = []
        for policy in policies:
            conditions = policy.get("conditions", {})
            users = conditions.get("users", {})
            apps = conditions.get("applications", {})
            client_app_types = set(conditions.get("clientAppTypes", []))
            grant_controls = policy.get("grantControls", {}) or {}

            # Check if policy targets all users
            include_users = users.get("includeUsers", [])
            targets_all_users = "All" in include_users

            # Check if policy targets all apps
            include_apps = apps.get("includeApplications", [])
            targets_all_apps = "All" in include_apps

            # Check if policy blocks legacy auth client types
            blocks_legacy = self.LEGACY_CLIENT_TYPES.issubset(client_app_types)

            # Check grant control
            built_in_controls = grant_controls.get("builtInControls", [])
            grant_control = "block" if "block" in built_in_controls else "allow"

            policy_data.append({
                "id": policy.get("id"),
                "display_name": policy.get("displayName"),
                "state": policy.get("state"),
                "targets_all_users": targets_all_users,
                "targets_all_apps": targets_all_apps,
                "blocks_legacy_auth": blocks_legacy,
                "client_app_types": list(client_app_types),
                "grant_control": grant_control,
            })

        return {
            "conditional_access_policies": policy_data,
            "total_policies": len(policy_data),
        }
