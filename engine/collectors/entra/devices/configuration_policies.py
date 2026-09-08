"""Intune Settings Catalog collector.

Essential Eight Benchmark Controls:
    E8-MAC-1.1, E8-MAC-1.2, E8-MAC-1.3, E8-MAC-1.4 (ML1 — Settings Catalog)
    E8-MAC-3.1, E8-MAC-3.3, E8-MAC-3.4 (ML3 — Settings Catalog)

E8-MAC-2.1 (ML2 — ASR rules) is handled separately by the asr_rules collector.

Connection Method: Microsoft Graph API
Required Scopes: DeviceManagementConfiguration.Read.All
Graph Endpoints:
    /beta/deviceManagement/configurationPolicies
    /beta/deviceManagement/configurationPolicies/{id}/settings
"""

from typing import Any

from collectors.base import BaseDataCollector
from collectors.graph_client import GraphClient


class ConfigurationPoliciesDataCollector(BaseDataCollector):
    """Collects Intune Settings Catalog policies for Essential Eight compliance evaluation.

    Retrieves Settings Catalog policies (VBA macro settings, AMSI scanning,
    internet macro blocking, signed-macro enforcement) needed to assess ASD
    Essential Eight Macro Settings controls at ML1 and ML3.
    """

    async def collect(self, client: GraphClient) -> dict[str, Any]:
        """Collect Intune Settings Catalog policy data.

        Returns:
            Dict containing:
            - configuration_policies: Settings Catalog policies with their settings
            - total_configuration_policies: Count of Settings Catalog policies
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

        return {
            "configuration_policies": policies_with_settings,
            "total_configuration_policies": len(policies_with_settings),
        }
