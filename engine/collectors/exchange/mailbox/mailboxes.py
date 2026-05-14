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
            upn = m.get("UserPrincipalName")
            sign_in_blocked: bool | None = None
            if upn:
                user = await client.run_cmdlet("ExchangeOnline", "Get-User", Identity=upn)
                if isinstance(user, dict):
                    block_credentials = user.get("BlockCredentials")
                    if block_credentials is not None:
                        sign_in_blocked = bool(block_credentials)

            mailboxes.append({
                "UserPrincipalName": upn,
                "DisplayName": m.get("DisplayName"),
                "PrimarySmtpAddress": m.get("PrimarySmtpAddress"),
                "SignInBlocked": sign_in_blocked,
            })

        return {
            "shared_mailboxes": mailboxes,
            "total_shared_mailboxes": len(mailboxes),
        }
