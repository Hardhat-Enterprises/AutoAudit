"""Authorization policy collector.

CIS Microsoft 365 Foundations Benchmark Controls:
    v6.0.0: 5.1.2.2, 5.1.2.3, 5.1.3.2, 5.1.4.6, 5.1.5.1, 5.1.6.2, 5.1.6.3

Connection Method: Microsoft Graph API
Required Scopes: Policy.Read.All
Graph Endpoint: /policies/authorizationPolicy
"""

from typing import Any

from collectors.base import BaseDataCollector
from collectors.graph_client import GraphClient


class AuthorizationPolicyDataCollector(BaseDataCollector):
    """Collects authorization policy settings for CIS compliance evaluation.

    This collector retrieves the authorization policy which contains default
    user role permissions, guest settings, and invitation settings.
    """

    async def collect(self, client: GraphClient) -> dict[str, Any]:
        """Collect authorization policy data.

        Returns:
            Dict containing:
            - authorization_policy: The authorization policy configuration
            - default_user_role_permissions: Default permissions for users
            - guest_invite_settings: Guest invitation settings
        """
        # Get authorization policy
        policy = await client.get("/policies/authorizationPolicy")

        # Extract default user role permissions
        default_permissions = policy.get("defaultUserRolePermissions", {})

        return {
            "authorization_policy": policy,
            "default_user_role_permissions": default_permissions,
            "allowed_to_create_apps": default_permissions.get("allowedToCreateApps"),
            "allowed_to_create_security_groups": default_permissions.get("allowedToCreateSecurityGroups"),
            "allowed_to_create_tenants": default_permissions.get("allowedToCreateTenants"),
            "allowed_to_read_bitlocker_keys_for_owned_device": default_permissions.get("allowedToReadBitlockerKeysForOwnedDevice"),
            "allowed_to_read_other_users": default_permissions.get("allowedToReadOtherUsers"),
            "guest_user_role_id": policy.get("guestUserRoleId"),
            "allow_invites_from": policy.get("allowInvitesFrom"),
            "allow_email_verified_users_to_join_organization": policy.get("allowEmailVerifiedUsersToJoinOrganization"),
            "block_msol_power_shell": policy.get("blockMsolPowerShell"),
        }
