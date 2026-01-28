"""Hosted connection filter collector.

CIS Microsoft 365 Foundations Benchmark Controls:
    v6.0.0: 2.1.12, 2.1.13

Connection Method: Exchange Online PowerShell (via Docker container)
Authentication: Client secret via MSAL -> access token passed to -AccessToken parameter
Required Cmdlets: Get-HostedConnectionFilterPolicy
Required Permissions: Exchange.ManageAsApp + Exchange role assignment
"""

from typing import Any

from collectors.powershell_base import BasePowerShellCollector
from collectors.powershell_client import PowerShellClient


class HostedConnectionFilterDataCollector(BasePowerShellCollector):
    """Collects connection filter policy for CIS compliance evaluation.

    This collector retrieves IP allow list and safe list settings
    to verify connection filtering is properly configured.
    """

    async def collect(self, client: PowerShellClient) -> dict[str, Any]:
        """Collect hosted connection filter data.

        Returns:
            Dict containing:
            - connection_filter_policies: List of connection filter policies
            - ip_allow_list: IP addresses in allow list
            - enable_safe_list: Safe list status
        """
        policies = await client.run_cmdlet(
            "ExchangeOnline", "Get-HostedConnectionFilterPolicy"
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
            "connection_filter_policies": policies,
            "total_policies": len(policies),
            "default_policy": default_policy,
            "ip_allow_list": default_policy.get("IPAllowList", []) if default_policy else [],
            "enable_safe_list": default_policy.get("EnableSafeList") if default_policy else None,
        }
