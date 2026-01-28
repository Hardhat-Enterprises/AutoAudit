"""Enrollment restrictions collector.

CIS Microsoft 365 Foundations Benchmark Controls:
    v6.0.0: 4.2

Connection Method: Microsoft Graph API
Required Scopes: DeviceManagementServiceConfig.Read.All
Graph Endpoint: /deviceManagement/deviceEnrollmentConfigurations
"""

from typing import Any

from collectors.base import BaseDataCollector
from collectors.graph_client import GraphClient


class EnrollmentRestrictionsDataCollector(BaseDataCollector):
    """Collects device enrollment restrictions for CIS compliance evaluation.

    This collector retrieves device enrollment restriction configurations
    to verify personal device enrollment is properly restricted.
    """

    async def collect(self, client: GraphClient) -> dict[str, Any]:
        """Collect enrollment restriction data.

        Returns:
            Dict containing:
            - enrollment_configurations: List of enrollment configurations
            - platform_restrictions: Platform-specific enrollment restrictions
            - personal_device_restrictions: Personal device enrollment settings
        """
        # Get device enrollment configurations
        configs = await client.get_all_pages(
            "/deviceManagement/deviceEnrollmentConfigurations",
            beta=True,
        )

        # Categorize configurations by type
        platform_restrictions = []
        limit_restrictions = []
        other_configs = []

        for config in configs:
            config_type = config.get("@odata.type", "")
            if "platformRestrictions" in config_type.lower():
                platform_restrictions.append(config)
            elif "limit" in config_type.lower():
                limit_restrictions.append(config)
            else:
                other_configs.append(config)

        # Check if personal device enrollment is blocked
        personal_devices_blocked = False
        for restriction in platform_restrictions:
            # Check platform restriction settings
            platforms = ["androidRestriction", "iosRestriction", "windowsRestriction", "macOSRestriction"]
            for platform in platforms:
                platform_config = restriction.get(platform, {})
                if platform_config.get("personalDeviceEnrollmentBlocked"):
                    personal_devices_blocked = True
                    break

        return {
            "enrollment_configurations": configs,
            "total_configurations": len(configs),
            "platform_restrictions": platform_restrictions,
            "limit_restrictions": limit_restrictions,
            "other_configurations": other_configs,
            "personal_devices_blocked": personal_devices_blocked,
        }
