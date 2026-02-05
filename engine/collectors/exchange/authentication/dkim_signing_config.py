"""DKIM signing config collector.

CIS Microsoft 365 Foundations Benchmark Controls:
    v6.0.0: 2.1.9

Connection Method: Exchange Online PowerShell (via Docker container)
Authentication: Client secret via MSAL -> access token passed to -AccessToken parameter
Required Cmdlets: Get-DkimSigningConfig
Required Permissions: Exchange.ManageAsApp + Exchange role assignment
"""

from typing import Any

from collectors.powershell_base import BasePowerShellCollector
from collectors.powershell_client import PowerShellClient


class DkimSigningConfigDataCollector(BasePowerShellCollector):
    """Collects DKIM signing configuration for CIS compliance evaluation.

    This collector retrieves DKIM signing status for all domains
    to verify email authentication is properly configured.
    """

    async def collect(self, client: PowerShellClient) -> dict[str, Any]:
        """Collect DKIM signing config data.

        Returns:
            Dict containing:
            - dkim_configs: List of DKIM configurations per domain
            - domains_with_dkim_enabled: Domains with DKIM enabled
            - domains_with_dkim_disabled: Domains without DKIM enabled
        """
        configs = await client.run_cmdlet("ExchangeOnline", "Get-DkimSigningConfig")

        # Handle None, single config, or list
        if configs is None:
            configs = []
        elif isinstance(configs, dict):
            configs = [configs]

        domains_enabled = [c.get("Domain") for c in configs if c.get("Enabled")]
        domains_disabled = [c.get("Domain") for c in configs if not c.get("Enabled")]

        return {
            "dkim_configs": configs,
            "total_domains": len(configs),
            "domains_with_dkim_enabled": domains_enabled,
            "domains_with_dkim_disabled": domains_disabled,
        }
