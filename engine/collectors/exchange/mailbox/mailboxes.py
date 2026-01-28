"""Mailboxes collector.

CIS Microsoft 365 Foundations Benchmark Controls:
    v6.0.0: 1.2.2

Connection Method: Exchange Online PowerShell (via Docker container)
Authentication: Client secret via MSAL -> access token passed to -AccessToken parameter
Required Cmdlets: Get-EXOMailbox
Required Permissions: Exchange.ManageAsApp + Exchange role assignment
"""

from typing import Any

from collectors.powershell_base import BasePowerShellCollector
from collectors.powershell_client import PowerShellClient


class MailboxesDataCollector(BasePowerShellCollector):
    """Collects mailbox information for CIS compliance evaluation.

    This collector retrieves shared mailboxes to verify
    shared mailboxes have appropriate sign-in settings.
    """

    async def collect(self, client: PowerShellClient) -> dict[str, Any]:
        """Collect mailbox data.

        Returns:
            Dict containing:
            - shared_mailboxes: List of shared mailboxes
            - total_shared_mailboxes: Count of shared mailboxes
        """
        # Get shared mailboxes only (RecipientTypeDetails -eq 'SharedMailbox')
        mailboxes = await client.run_cmdlet(
            "ExchangeOnline",
            "Get-EXOMailbox",
            RecipientTypeDetails="SharedMailbox",
            ResultSize="Unlimited",
        )

        # Handle None, single result, or list
        if mailboxes is None:
            mailboxes = []
        elif isinstance(mailboxes, dict):
            mailboxes = [mailboxes]

        return {
            "shared_mailboxes": mailboxes,
            "total_shared_mailboxes": len(mailboxes),
        }
