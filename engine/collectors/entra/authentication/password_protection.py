"""Password protection collector.

CIS Microsoft 365 Foundations Benchmark Controls:
    v6.0.0: 5.2.3.2, 5.2.3.3

Connection Method: Microsoft Graph API
Required Scopes: Directory.Read.All
Graph Endpoint: /settings (directory settings)
"""

from typing import Any

from collectors.base import BaseDataCollector
from collectors.graph_client import GraphClient


class PasswordProtectionDataCollector(BaseDataCollector):
    """Collects password protection settings for CIS compliance evaluation.

    This collector retrieves custom banned password list configuration
    and on-premises password protection settings.
    """

    async def collect(self, client: GraphClient) -> dict[str, Any]:
        """Collect password protection data.

        Returns:
            Dict containing:
            - password_protection_settings: Password protection configuration
            - banned_password_list_enabled: Whether custom banned list is enabled
            - on_prem_protection_enabled: Whether on-prem protection is enabled
            - lockout_settings: Account lockout configuration
        """
        # Get directory settings which include password rule settings
        settings_response = await client.get("/settings", beta=True)
        settings_list = settings_response.get("value", [])

        # Find the password rule settings template
        password_settings = None
        for setting in settings_list:
            if setting.get("templateId") == "5cf42378-d67d-4f36-ba46-e8b86229381d":
                # Password Rule Settings
                password_settings = setting
                break

        # Extract values from settings
        values = {}
        if password_settings:
            for value in password_settings.get("values", []):
                values[value.get("name")] = value.get("value")

        return {
            "password_protection_settings": password_settings,
            "settings_values": values,
            "banned_password_list_enabled": values.get("EnableBannedPasswordCheck") == "True",
            "banned_password_list": values.get("BannedPasswordList"),
            "on_prem_protection_enabled": values.get("EnableBannedPasswordCheckOnPremises") == "True",
            "lockout_threshold": values.get("LockoutThreshold"),
            "lockout_duration_in_seconds": values.get("LockoutDurationInSeconds"),
            "enforce_custom_banned_passwords": values.get("BannedPasswordCheckOnPremisesMode"),
        }
