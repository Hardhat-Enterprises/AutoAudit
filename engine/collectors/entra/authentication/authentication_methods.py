"""Authentication methods collector.

CIS Microsoft 365 Foundations Benchmark Controls:
    v6.0.0: 5.2.3.1, 5.2.3.5, 5.2.3.6, 5.2.3.7

Connection Method: Microsoft Graph API
Required Scopes: Policy.Read.All, Policy.Read.AuthenticationMethod
Graph Endpoint: /policies/authenticationMethodsPolicy
"""

from typing import Any

from collectors.base import BaseDataCollector
from collectors.graph_client import GraphClient


class AuthenticationMethodsDataCollector(BaseDataCollector):
    """Collects authentication method configurations for CIS compliance evaluation.

    This collector retrieves authentication method policies including
    SMS, Voice, Email OTP, and other method configurations.
    """

    async def collect(self, client: GraphClient) -> dict[str, Any]:
        """Collect authentication methods policy data.

        Returns:
            Dict containing:
            - authentication_methods_policy: The authentication methods policy
            - method_configurations: Individual method configurations
            - sms_enabled: Whether SMS authentication is enabled
            - voice_enabled: Whether voice call authentication is enabled
            - email_otp_enabled: Whether email OTP is enabled
        """
        # Get the authentication methods policy
        policy = await client.get("/policies/authenticationMethodsPolicy", beta=True)

        # Get individual method configurations
        method_configs = policy.get("authenticationMethodConfigurations", [])

        # Build lookup by method type
        methods_by_type = {}
        for config in method_configs:
            method_id = config.get("id", "")
            methods_by_type[method_id] = config

        # Check specific method states
        def is_method_enabled(method_id: str) -> bool | None:
            method = methods_by_type.get(method_id)
            if method is None:
                return None
            return method.get("state") == "enabled"

        return {
            "authentication_methods_policy": policy,
            "method_configurations": method_configs,
            "methods_by_type": methods_by_type,
            "sms_enabled": is_method_enabled("Sms"),
            "voice_enabled": is_method_enabled("Voice"),
            "email_otp_enabled": is_method_enabled("Email"),
            "fido2_enabled": is_method_enabled("Fido2"),
            "microsoft_authenticator_enabled": is_method_enabled("MicrosoftAuthenticator"),
            "temporary_access_pass_enabled": is_method_enabled("TemporaryAccessPass"),
            "software_oath_enabled": is_method_enabled("SoftwareOath"),
            "hardware_oath_enabled": is_method_enabled("HardwareOath"),
        }
