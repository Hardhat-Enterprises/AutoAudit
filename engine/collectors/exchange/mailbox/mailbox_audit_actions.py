"""Mailbox audit actions collector.

CIS Microsoft 365 Foundations Benchmark Controls:
    v6.0.0: 6.1.2

Control Description:
    6.1.2 - Ensure mailbox auditing for all users is Enabled

Connection Method: Exchange Online PowerShell (via Docker container)
Authentication: Client secret via MSAL -> access token passed to -AccessToken parameter
Required Cmdlets: Get-EXOMailbox
Required Permissions: Exchange.ManageAsApp + Exchange role assignment
"""

from typing import Any

from collectors.powershell_base import BasePowerShellCollector
from collectors.powershell_client import PowerShellClient


class MailboxAuditActionsDataCollector(BasePowerShellCollector):
    """Collects mailbox audit action configuration for CIS 6.1.2 evaluation.

    This collector retrieves audit action settings (AuditAdmin, AuditDelegate,
    AuditOwner) for user mailboxes.
    """

    async def collect(self, client: PowerShellClient) -> dict[str, Any]:
        """Collect mailbox audit action configuration.

        Returns:
            Dict containing:
            - mailboxes: List of user mailboxes with audit settings
            - total_user_mailboxes: Total number of user mailboxes
        """
        # Get user mailboxes with audit properties
        # Filter in PowerShell and select only needed properties to reduce output
        cmdlet = (
            "Get-EXOMailbox -PropertySets Audit, Minimum -ResultSize Unlimited "
            "-WarningAction SilentlyContinue | "
            "Where-Object { $_.RecipientTypeDetails -eq 'UserMailbox' } | "
            "Select-Object UserPrincipalName, AuditEnabled, AuditAdmin, AuditDelegate, AuditOwner"
        )
        mailboxes = await client.run_cmdlet("ExchangeOnline", cmdlet)

        # Handle None, single result, or list
        if mailboxes is None:
            mailboxes = []
        elif isinstance(mailboxes, dict):
            mailboxes = [mailboxes]

        return {
            "mailboxes": mailboxes,
            "total_user_mailboxes": len(mailboxes),
        }
