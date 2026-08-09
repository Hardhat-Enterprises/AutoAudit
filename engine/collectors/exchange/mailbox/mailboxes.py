"""Mailboxes collector.

CIS Microsoft 365 Foundations Benchmark Controls:
    v6.0.0: 1.2.2

Connection Method: Exchange Online PowerShell (via Docker container)
Authentication: Client secret via MSAL -> access token passed to -AccessToken parameter
Required Cmdlets: Get-EXOMailbox, Get-User
Required Permissions: Exchange.ManageAsApp + Exchange role assignment
"""

from typing import Any

from collectors.powershell_base import BasePowerShellCollector
from collectors.powershell_client import PowerShellClient


class MailboxesDataCollector(BasePowerShellCollector):
    """Collects mailbox information for CIS compliance evaluation."""

    async def collect(self, client: PowerShellClient) -> dict[str, Any]:
        """Collect shared mailboxes and their associated user information."""

        mailboxes = await client.run_cmdlet(
            "ExchangeOnline",
            "Get-EXOMailbox",
            RecipientTypeDetails="SharedMailbox",
            ResultSize="Unlimited",
        )

        if mailboxes is None:
            mailboxes = []
        elif isinstance(mailboxes, dict):
            mailboxes = [mailboxes]

        enriched_mailboxes = []

        for mailbox in mailboxes:
            user_principal_name = mailbox.get("UserPrincipalName")
            user_account = None

            if user_principal_name:
                user_account = await client.run_cmdlet(
                    "ExchangeOnline",
                    "Get-User",
                    Identity=user_principal_name,
                )

            enriched_mailboxes.append(
            {
                "display_name": mailbox.get("DisplayName"),
                "user_principal_name": mailbox.get("UserPrincipalName"),
                "external_directory_object_id": mailbox.get(
                    "ExternalDirectoryObjectId"
                ),
                "account_disabled": (
                    user_account.get("AccountDisabled")
                    if isinstance(user_account, dict)
                    else None
                ),
            }
        )

        return {
            "shared_mailboxes": enriched_mailboxes,
            "total_shared_mailboxes": len(enriched_mailboxes),
        }
