"""Transport config collector.

CIS Microsoft 365 Foundations Benchmark Controls:
    v6.0.0: 6.5.4

Connection Method: Exchange Online PowerShell (via Docker container)
Authentication: Client secret via MSAL -> access token passed to -AccessToken parameter
Required Cmdlets: Get-TransportConfig
Required Permissions: Exchange.ManageAsApp + Exchange role assignment
"""

from typing import Any

from collectors.powershell_base import BasePowerShellCollector
from collectors.powershell_client import PowerShellClient


class TransportConfigDataCollector(BasePowerShellCollector):
    """Collects transport config for CIS compliance evaluation.

    This collector retrieves SMTP client authentication settings
    at the organization level.
    """

    async def collect(self, client: PowerShellClient) -> dict[str, Any]:
        """Collect transport configuration data.

        Returns:
            Dict containing:
            - transport_config: Full transport configuration
            - smtp_client_authentication_disabled: SMTP client auth status (CIS 6.5.4)
        """
        config = await client.run_cmdlet("ExchangeOnline", "Get-TransportConfig")

        return {
            "transport_config": config,
            "smtp_client_authentication_disabled": config.get("SmtpClientAuthenticationDisabled"),
        }
