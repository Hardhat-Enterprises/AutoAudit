"""Mailbox audit bypass collector.

CIS Microsoft 365 Foundations Benchmark Controls:
    v6.0.0: 6.1.3

Control Description:
    6.1.3 - Ensure mailbox audit logging bypass is not enabled

Connection Method: Exchange Online PowerShell (via Docker container)
Authentication: Client secret via MSAL -> access token passed to -AccessToken parameter
Required Cmdlets: Get-MailboxAuditBypassAssociation
Required Permissions: Exchange.ManageAsApp + Exchange role assignment
"""

from typing import Any

from collectors.powershell_base import BasePowerShellCollector
from collectors.powershell_client import PowerShellClient


class MailboxAuditDataCollector(BasePowerShellCollector):
    """Collects mailbox audit bypass associations for CIS 6.1.3 evaluation.

    This collector retrieves mailboxes that have audit bypass enabled.
    """

    async def collect(self, client: PowerShellClient) -> dict[str, Any]:
        """Collect mailbox audit bypass data.

        Returns:
            Dict containing:
            - accounts_with_bypass_enabled: List of accounts with AuditBypassEnabled = True
            - bypass_count: Number of accounts with bypass enabled
        """
        # Get only mailboxes with AuditBypassEnabled = True
        # Filter in PowerShell to avoid large output and suppress warnings
        cmdlet = (
            "Get-MailboxAuditBypassAssociation -ResultSize Unlimited "
            "-WarningAction SilentlyContinue | "
            "Where-Object { $_.AuditBypassEnabled -eq $true } | "
            "Select-Object Name, AuditBypassEnabled"
        )
        bypassed = await client.run_cmdlet("ExchangeOnline", cmdlet)

        # Handle None, single result, or list
        if bypassed is None:
            bypassed = []
        elif isinstance(bypassed, dict):
            bypassed = [bypassed]

        return {
            "accounts_with_bypass_enabled": bypassed,
            "bypass_count": len(bypassed),
        }
