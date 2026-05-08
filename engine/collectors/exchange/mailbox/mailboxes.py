from typing import TYPE_CHECKING, Any

from collectors.powershell_base import BasePowerShellCollector

if TYPE_CHECKING:
    from collectors.powershell_client import PowerShellClient


class MailboxesDataCollector(BasePowerShellCollector):

    async def collect(self, client: "PowerShellClient") -> dict[str, Any]:
        raw = await client.run_cmdlet(
            "ExchangeOnline",
            "Get-EXOMailbox",
            RecipientTypeDetails="SharedMailbox",
            ResultSize="Unlimited",
        )

        if raw is None:
            raw = []
        elif isinstance(raw, dict):
            raw = [raw]

        mailboxes: list[dict[str, Any]] = []
        for m in raw:
            account_enabled = m.get("AccountEnabled")
            mailboxes.append({
                "UserPrincipalName": m.get("UserPrincipalName"),
                "DisplayName": m.get("DisplayName"),
                "PrimarySmtpAddress": m.get("PrimarySmtpAddress"),
                "AccountEnabled": account_enabled,
                "SignInBlocked": None if account_enabled is None else (not account_enabled),
            })

        return {
            "shared_mailboxes": mailboxes,
            "total_shared_mailboxes": len(mailboxes),
        }
