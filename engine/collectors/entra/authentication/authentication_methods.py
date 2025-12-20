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
        # TODO: Implement collector
        raise NotImplementedError("Collector not yet implemented")
