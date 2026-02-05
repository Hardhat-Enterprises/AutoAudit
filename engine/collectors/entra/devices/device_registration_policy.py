"""Device registration policy collector.

CIS Microsoft 365 Foundations Benchmark Controls:
    v6.0.0: 5.1.4.1, 5.1.4.2, 5.1.4.3, 5.1.4.4, 5.1.4.5

Connection Method: Microsoft Graph API
Required Scopes: Policy.Read.DeviceConfiguration
Graph Endpoint: /policies/deviceRegistrationPolicy
"""

from typing import Any

from collectors.base import BaseDataCollector
from collectors.graph_client import GraphClient


class DeviceRegistrationPolicyDataCollector(BaseDataCollector):
    """Collects device registration policy for CIS compliance evaluation.

    This collector retrieves device join settings, LAPS configuration,
    and local admin assignment settings for compliance evaluation.
    """

    async def collect(self, client: GraphClient) -> dict[str, Any]:
        """Collect device registration policy data.

        Returns:
            Dict containing:
            - device_registration_policy: The device registration policy
            - azure_ad_join_settings: Azure AD join configuration
            - local_admin_settings: Local admin assignment settings
            - laps_settings: LAPS configuration
        """
        # Get device registration policy
        policy = await client.get("/policies/deviceRegistrationPolicy", beta=True)

        # Extract key settings
        azure_ad_join = policy.get("azureADJoin", {})
        azure_ad_registration = policy.get("azureADRegistration", {})
        local_admin_password = policy.get("localAdminPassword", {})

        return {
            "device_registration_policy": policy,
            "azure_ad_join_settings": azure_ad_join,
            "azure_ad_join_allowed": azure_ad_join.get("isAdminConfigurable"),
            "azure_ad_join_allowed_users": azure_ad_join.get("allowedUsers"),
            "azure_ad_join_allowed_groups": azure_ad_join.get("allowedGroups"),
            "azure_ad_registration_settings": azure_ad_registration,
            "azure_ad_registration_allowed": azure_ad_registration.get("isAdminConfigurable"),
            "local_admin_password_settings": local_admin_password,
            "laps_enabled": local_admin_password.get("isEnabled"),
            "user_device_quota": policy.get("userDeviceQuota"),
            "multi_factor_auth_configuration": policy.get("multiFactorAuthConfiguration"),
        }
