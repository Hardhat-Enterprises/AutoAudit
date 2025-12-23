"""Organization config collector.

CIS Microsoft 365 Foundations Benchmark Controls:
    v6.0.0: 1.3.6, 1.3.9, 6.1.1, 6.5.1, 6.5.2, 6.5.4, 6.5.5

Control Descriptions:
    1.3.6 - Ensure Customer Lockbox is enabled
    1.3.9 - Ensure OAuth authentication is enabled
    6.1.1 - Ensure AuditDisabled is set to False (mailbox auditing at org level)
    6.5.1 - Ensure SMTP AUTH is disabled
    6.5.2 - Ensure all senders are notified when mail is blocked
    6.5.4 - Ensure Direct Send is disabled
    6.5.5 - Ensure IMAP is disabled for all users

Connection Method: Exchange Online PowerShell (via Docker container)
Authentication: Client secret via MSAL -> access token passed to -AccessToken parameter
Required Cmdlets: Get-OrganizationConfig
Required Permissions: Exchange.ManageAsApp + Exchange role assignment
"""

from typing import Any

from collectors.powershell_base import BasePowerShellCollector
from collectors.powershell_client import PowerShellClient


class OrganizationConfigDataCollector(BasePowerShellCollector):
    """Collects organization config for CIS compliance evaluation.

    This collector retrieves Exchange organization configuration including
    customer lockbox, OAuth, audit settings, SMTP AUTH, and Direct Send settings.
    """

    async def collect(self, client: PowerShellClient) -> dict[str, Any]:
        """Collect organization configuration data.

        Returns:
            Dict containing:
            - organization_config: Full organization configuration
            - customer_lockbox_enabled: Customer lockbox status (CIS 1.3.6)
            - oauth_enabled: OAuth authentication status
            - audit_disabled: Whether audit is disabled (CIS 6.1.1)
            - smtp_client_auth_disabled: SMTP client auth status (CIS 6.5.1)
        """
        config = await client.run_cmdlet("ExchangeOnline", "Get-OrganizationConfig")

        return {
            "organization_config": config,
            "customer_lockbox_enabled": config.get("CustomerLockBoxEnabled"),
            "oauth_enabled": config.get("OAuth2ClientProfileEnabled"),
            "audit_disabled": config.get("AuditDisabled"),
            "smtp_client_auth_disabled": config.get("SmtpClientAuthenticationDisabled"),
        }
