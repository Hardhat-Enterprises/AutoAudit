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
    """Collects device registration policy for CIS compliance evaluation."""

    async def collect(self, client: GraphClient) -> dict[str, Any]:
        """Collect device registration policy data.

        Returns:
            Dict containing device join settings, quota, local admin config, and LAPS state.
        """
        policy = await client.get("/policies/deviceRegistrationPolicy", beta=True)

        azure_ad_join = policy.get("azureADJoin", {}) or {}
        azure_ad_registration = policy.get("azureADRegistration", {}) or {}
        local_admin_password = policy.get("localAdminPassword", {}) or {}
        local_admins_config = azure_ad_join.get("localAdmins", {}) or {}

        reg_users_raw = local_admins_config.get("registeringUsers")
        if isinstance(reg_users_raw, dict):
            odata_type = reg_users_raw.get("@odata.type", "")
            if "noDeviceRegistrationMembership" in odata_type:
                registering_users_local_admin: str | None = "notAllowed"
            elif "allDeviceRegistrationMembership" in odata_type:
                registering_users_local_admin = "allowed"
            else:
                registering_users_local_admin = odata_type or None
        else:
            registering_users_local_admin = reg_users_raw

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
            "local_admins_config": local_admins_config,
            "global_admins_enabled_on_join": local_admins_config.get("enableGlobalAdmins"),
            "registering_users_local_admin": registering_users_local_admin,
        }
