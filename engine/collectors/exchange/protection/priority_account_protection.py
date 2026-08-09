"""Priority account protection collector.

CIS Microsoft 365 Foundations Benchmark Controls:
    v6.0.0: 2.4.1, 2.4.2

Connection Method: Exchange Online PowerShell (via Docker container)
Authentication: Client secret via MSAL -> access token passed to -AccessToken parameter
Required Cmdlets: Get-EmailTenantSettings, Get-User
Required Permissions: Exchange.ManageAsApp + Exchange role assignment
"""

from typing import Any

from collectors.powershell_base import BasePowerShellCollector
from collectors.powershell_client import PowerShellClient


class PriorityAccountProtectionDataCollector(BasePowerShellCollector):
    """Collects priority account protection configuration for CIS compliance evaluation.

    This collector retrieves the tenant-wide Priority account protection toggle,
    and the list of individual accounts tagged as priority (VIP) accounts.
    """

    async def collect(self, client: PowerShellClient) -> dict[str, Any]:
        """Collect priority account protection data.

        Returns:
            Dict containing:
            - protection_enabled: Whether Priority account protection is turned on
            - priority_accounts: List of accounts tagged as priority (VIP) accounts
            - total_priority_accounts: Number of priority accounts
        """

        #tenant_settings is required for v6.0.0 control 2.4.1
        #accounts is required for v6.0.0 control 2.4.2
        tenant_settings = await client.run_cmdlet("ExchangeOnline", "Get-EmailTenantSettings")
        accounts = await client.run_cmdlet("ExchangeOnline", "Get-User", IsVIP=True)

        # Handle no accounts, a single account, or a list of accounts
        if accounts is None:
            accounts = []
        elif isinstance(accounts, dict):
            accounts = [accounts]

        return {
            "protection_enabled": (
                tenant_settings.get("EnablePriorityAccountProtection")
                if tenant_settings
                else None
            ),
            "priority_accounts": accounts,
            "total_priority_accounts": len(accounts),
        }