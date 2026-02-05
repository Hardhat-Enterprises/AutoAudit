"""Teams protection policy collector.

CIS Microsoft 365 Foundations Benchmark Controls:
    v6.0.0: 2.4.4

Connection Method: Exchange Online PowerShell (via Docker container)
Authentication: Client secret via MSAL -> access token passed to -AccessToken parameter
Required Cmdlets: Get-TeamsProtectionPolicy
Required Permissions: Exchange.ManageAsApp + Exchange role assignment
"""

from typing import Any

from collectors.powershell_base import BasePowerShellCollector
from collectors.powershell_client import PowerShellClient


class TeamsProtectionPolicyDataCollector(BasePowerShellCollector):
    """Collects Teams protection policy for CIS compliance evaluation.

    This collector retrieves zero-hour auto purge settings for Teams
    to verify protection against malicious content.
    """

    async def collect(self, client: PowerShellClient) -> dict[str, Any]:
        """Collect Teams protection policy data.

        Returns:
            Dict containing:
            - teams_protection_policy: The Teams protection policy
            - zap_enabled: Zero-hour auto purge status for Teams
        """
        policy = await client.run_cmdlet("ExchangeOnline", "Get-TeamsProtectionPolicy")

        return {
            "teams_protection_policy": policy,
            "zap_enabled": policy.get("ZapEnabled") if policy else None,
            "malware_scan_enabled": policy.get("MalwareScanEnabled") if policy else None,
        }
