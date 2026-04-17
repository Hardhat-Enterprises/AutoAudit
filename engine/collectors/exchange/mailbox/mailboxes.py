"""Mailboxes collector.

CIS Microsoft 365 Foundations Benchmark Controls:
    v6.0.0: 1.2.2

Control Description:
    1.2.2 - Ensure sign-in to shared mailboxes is blocked

Connection Method: Exchange Online PowerShell (via Docker container)
Authentication: Client secret via MSAL -> access token passed to -AccessToken parameter
Required Cmdlets: Get-EXOMailbox, Get-User
Required Permissions: Exchange.ManageAsApp + Exchange role assignment
"""

from typing import Any

from collectors.powershell_base import BasePowerShellCollector
from collectors.powershell_client import PowerShellClient


class MailboxesDataCollector(BasePowerShellCollector):
    """Collects shared mailbox sign-in settings for CIS compliance evaluation.

    This collector retrieves all shared mailboxes and checks whether direct
    sign-in is blocked for each associated Entra account via Get-User
    BlockCredentials property.
    """

    async def collect(self, client: PowerShellClient) -> dict[str, Any]:
        cmdlet = (
            "Get-EXOMailbox -RecipientTypeDetails SharedMailbox -ResultSize Unlimited | "
            "ForEach-Object { "
            "$mbx = $_; "
            "$user = Get-User -Identity $mbx.UserPrincipalName -ErrorAction SilentlyContinue; "
            "[PSCustomObject]@{ "
            "UserPrincipalName = $mbx.UserPrincipalName; "
            "DisplayName = $mbx.DisplayName; "
            "PrimarySmtpAddress = $mbx.PrimarySmtpAddress; "
            "SignInBlocked = if ($user) { $user.BlockCredentials } else { $null } "
            "} }"
        )
        mailboxes = await client.run_cmdlet("ExchangeOnline", cmdlet)

        if mailboxes is None:
            mailboxes = []
        elif isinstance(mailboxes, dict):
            mailboxes = [mailboxes]

        signin_blocked = [m for m in mailboxes if m.get("SignInBlocked") is True]
        signin_allowed = [m for m in mailboxes if m.get("SignInBlocked") is not True]

        return {
            "shared_mailboxes": mailboxes,
            "total_shared_mailboxes": len(mailboxes),
            "mailboxes_with_signin_blocked": len(signin_blocked),
            "mailboxes_with_signin_allowed": len(signin_allowed),
        }
