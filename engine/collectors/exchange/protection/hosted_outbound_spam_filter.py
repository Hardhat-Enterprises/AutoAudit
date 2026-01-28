"""Hosted outbound spam filter collector.

CIS Microsoft 365 Foundations Benchmark Controls:
    v6.0.0: 2.1.6, 2.1.15, 6.2.1

Connection Method: Exchange Online PowerShell (via Docker container)
Authentication: Client secret via MSAL -> access token passed to -AccessToken parameter
Required Cmdlets: Get-HostedOutboundSpamFilterPolicy
Required Permissions: Exchange.ManageAsApp + Exchange role assignment
"""

from typing import Any

from collectors.powershell_base import BasePowerShellCollector
from collectors.powershell_client import PowerShellClient


class HostedOutboundSpamFilterDataCollector(BasePowerShellCollector):
    """Collects outbound spam filter policy for CIS compliance evaluation.

    This collector retrieves outbound spam notifications, message limits,
    and auto-forwarding settings for compliance evaluation.
    """

    async def collect(self, client: PowerShellClient) -> dict[str, Any]:
        """Collect hosted outbound spam filter data.

        Returns:
            Dict containing:
            - outbound_spam_policies: List of outbound spam filter policies
            - default_policy: The default policy
            - auto_forwarding_mode: Auto-forwarding configuration
        """
        policies = await client.run_cmdlet(
            "ExchangeOnline", "Get-HostedOutboundSpamFilterPolicy"
        )

        # Handle None, single policy, or list
        if policies is None:
            policies = []
        elif isinstance(policies, dict):
            policies = [policies]

        # Get default policy
        default_policy = next(
            (p for p in policies if p.get("IsDefault")),
            policies[0] if policies else None
        )

        return {
            "outbound_spam_policies": policies,
            "total_policies": len(policies),
            "default_policy": default_policy,
            "auto_forwarding_mode": default_policy.get("AutoForwardingMode") if default_policy else None,
            "bcc_suspicious_outbound_mail": default_policy.get("BccSuspiciousOutboundMail") if default_policy else None,
            "notify_outbound_spam": default_policy.get("NotifyOutboundSpam") if default_policy else None,
        }
