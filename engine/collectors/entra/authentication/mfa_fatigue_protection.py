"""MFA fatigue protection collector.

CIS Microsoft 365 Foundations Benchmark Controls:
    v6.0.0: 5.2.3.1

Connection Method: Microsoft Graph API
Required Scopes: Policy.Read.All
Graph Endpoint: /policies/authenticationMethodsPolicy/authenticationMethodConfigurations/MicrosoftAuthenticator

Control covered:
    - 5.2.3.1: Ensure Microsoft Authenticator is configured to protect against MFA fatigue
"""

from typing import Any

from collectors.base import BaseDataCollector
from collectors.graph_client import GraphClient


class MfaFatigueProtectionDataCollector(BaseDataCollector):
    """Collects Microsoft Authenticator MFA fatigue protection settings.

    This collector retrieves Microsoft Authenticator configuration to verify
    that number matching and additional context are enabled to protect
    against MFA fatigue attacks.
    """

    async def collect(self, client: GraphClient) -> dict[str, Any]:
        """Collect Microsoft Authenticator MFA fatigue protection settings.

        Returns:
            Dict containing:
            - authenticator_config: Full Microsoft Authenticator configuration
            - state: Whether Microsoft Authenticator is enabled/disabled
            - number_matching_enabled: Whether number matching is enabled
            - display_app_information_enabled: Whether app context is shown
            - display_location_information_enabled: Whether location context is shown
            - feature_settings: Detailed feature settings configuration
            - mfa_fatigue_protection_enabled: Overall assessment of MFA fatigue protection
        """
        # Get Microsoft Authenticator configuration
        config = await client.get(
            "/policies/authenticationMethodsPolicy/authenticationMethodConfigurations/MicrosoftAuthenticator",
            beta=True,
        )

        # Extract feature settings
        feature_settings = config.get("featureSettings", {})

        # Extract individual feature states
        number_matching_state = feature_settings.get("numberMatchingRequiredState", {})
        display_app_state = feature_settings.get("displayAppInformationRequiredState", {})
        display_location_state = feature_settings.get("displayLocationInformationRequiredState", {})

        # Determine if features are enabled
        # State can be "enabled", "disabled", or "default"
        number_matching_enabled = number_matching_state.get("state") == "enabled"
        display_app_enabled = display_app_state.get("state") == "enabled"
        display_location_enabled = display_location_state.get("state") == "enabled"

        # MFA fatigue protection is considered enabled if number matching is enabled
        # Additional context (app info, location) provides extra protection
        mfa_fatigue_protection_enabled = number_matching_enabled

        return {
            "authenticator_config": config,
            "state": config.get("state"),
            "number_matching_enabled": number_matching_enabled,
            "number_matching_state": number_matching_state,
            "display_app_information_enabled": display_app_enabled,
            "display_app_information_state": display_app_state,
            "display_location_information_enabled": display_location_enabled,
            "display_location_information_state": display_location_state,
            "feature_settings": feature_settings,
            "mfa_fatigue_protection_enabled": mfa_fatigue_protection_enabled,
            "include_targets": config.get("includeTargets", []),
            "exclude_targets": config.get("excludeTargets", []),
        }
