"""Device management settings collector.

CIS Microsoft 365 Foundations Benchmark Controls:
    v6.0.0: 4.1

Connection Method: Microsoft Graph API
Required Scopes: DeviceManagementConfiguration.Read.All
Graph Endpoint: /deviceManagement/settings
"""

from typing import Any

from collectors.base import BaseDataCollector
from collectors.graph_client import GraphClient


class DeviceManagementSettingsDataCollector(BaseDataCollector):
    """Collects Intune device management settings for CIS compliance evaluation.

    This collector retrieves Intune compliance policy default settings
    to verify proper device management configuration.
    """

    async def collect(self, client: GraphClient) -> dict[str, Any]:
        """Collect device management settings data.

        Returns:
            Dict containing:
            - device_management_settings: The device management settings
            - compliance_policy_defaults: Default compliance policy settings
        """
        # Get device management settings
        settings = await client.get("/deviceManagement/settings", beta=True)

        # Get device compliance policy setting state summary
        try:
            compliance_settings = await client.get(
                "/deviceManagement/deviceCompliancePolicySettingStateSummaries",
                beta=True,
            )
        except Exception:
            compliance_settings = {}

        return {
            "device_management_settings": settings,
            "device_compliance_on_boarded": settings.get("deviceComplianceCheckinThresholdDays"),
            "is_scheduled_action_enabled": settings.get("isScheduledActionEnabled"),
            "secure_by_default": settings.get("secureByDefault"),
            "compliance_policy_summaries": compliance_settings.get("value", []),
        }
