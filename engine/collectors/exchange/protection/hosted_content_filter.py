"""Hosted content filter collector.

CIS Microsoft 365 Foundations Benchmark Controls:
    v6.0.0: 2.1.14

Connection Method: Exchange Online PowerShell (via Docker container)
Authentication: Client secret via MSAL -> access token passed to -AccessToken parameter
Required Cmdlets: Get-HostedContentFilterPolicy
Required Permissions: Exchange.ManageAsApp + Exchange role assignment
"""

from typing import Any

from collectors.powershell_base import BasePowerShellCollector
from collectors.powershell_client import PowerShellClient


class HostedContentFilterDataCollector(BasePowerShellCollector):
    """Collects content filter policy for CIS compliance evaluation.

    This collector retrieves allowed sender domains configuration
    to verify content filtering is properly configured.
    """

    async def collect(self, client: PowerShellClient) -> dict[str, Any]:
        """Collect hosted content filter data.

        Returns:
            Dict containing:
            - content_filter_policies: List of content filter policies
            - allowed_sender_domains: Domains allowed to bypass filtering
            - allowed_senders: Senders allowed to bypass filtering
        """
        policies = await client.run_cmdlet(
            "ExchangeOnline", "Get-HostedContentFilterPolicy"
        )

        # Handle None, single policy, or list
        if policies is None:
            policies = []
        elif isinstance(policies, dict):
            policies = [policies]

        # Get default policy settings
        default_policy = next(
            (p for p in policies if p.get("IsDefault")),
            policies[0] if policies else None
        )

        return {
            "content_filter_policies": policies,
            "total_policies": len(policies),
            "default_policy": default_policy,
            "allowed_sender_domains": default_policy.get("AllowedSenderDomains", []) if default_policy else [],
            "allowed_senders": default_policy.get("AllowedSenders", []) if default_policy else [],
        }
