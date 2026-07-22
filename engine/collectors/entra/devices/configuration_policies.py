"""Intune configuration policies collector.

Essential Eight Benchmark Controls:
    E8-MAC-1.1, E8-MAC-1.2, E8-MAC-1.3, E8-MAC-1.4 (ML1 — Settings Catalog)
    E8-MAC-2.1 (ML2 — Legacy Device Configuration / ASR rules)
    E8-MAC-3.1, E8-MAC-3.3, E8-MAC-3.4 (ML3 — Settings Catalog)

Connection Method: Microsoft Graph API
Required Scopes: DeviceManagementConfiguration.Read.All
Graph Endpoints:
    /beta/deviceManagement/configurationPolicies
    /beta/deviceManagement/configurationPolicies/{id}/settings
    /v1.0/deviceManagement/deviceConfigurations
"""

from typing import Any

from collectors.base import BaseDataCollector
from collectors.graph_client import GraphClient


class ConfigurationPoliciesDataCollector(BaseDataCollector):
    """Collects Intune configuration policies for Essential Eight compliance evaluation.

    Retrieves Settings Catalog policies (VBA macro settings, AMSI scanning,
    internet macro blocking, V3 signatures) and Legacy Device Configuration
    profiles (ASR rules) needed to assess ASD Essential Eight Macro Settings
    controls across ML1-ML3.
    """

    async def collect(self, client: GraphClient) -> dict[str, Any]:
        """Collect Intune configuration policy data.

        Returns:
            Dict containing:
            - configuration_policies: Settings Catalog policies with their settings
            - total_configuration_policies: Count of Settings Catalog policies
            - device_configurations: Legacy Device Configuration profiles (includes ASR rules)
            - total_device_configurations: Count of Legacy Device Configuration profiles
        """
        # Settings Catalog policies — covers ML1 (E8-MAC-1.1 to 1.4) and ML3 controls
        policies = await client.get_all_pages(
            "/deviceManagement/configurationPolicies",
            beta=True,
        )

        # Fetch the configured setting values for each policy individually.
        # The top-level policy list only returns metadata (name, description, assignments).
        # The actual setting IDs and values are in a separate per-policy endpoint.
        policies_with_settings = []
        for policy in policies:
            policy_id = policy.get("id")
            if not policy_id:
                continue
            settings = await client.get_all_pages(
                f"/deviceManagement/configurationPolicies/{policy_id}/settings",
                beta=True,
            )
            policies_with_settings.append({
                **policy,
                "settings": settings,
            })

        # Legacy Device Configuration profiles — covers ML2 (E8-MAC-2.1, ASR rules).
        # Uses v1.0 endpoint, not beta. ASR rule state (block/audit/off) is readable
        # directly from the windowsDefenderAdvancedThreatProtectionConfiguration object.
        device_configurations = await client.get_all_pages(
            "/deviceManagement/deviceConfigurations",
            beta=False,
        )

        return {
            "configuration_policies": policies_with_settings,
            "total_configuration_policies": len(policies_with_settings),
            "device_configurations": device_configurations,
            "total_device_configurations": len(device_configurations),
        }
