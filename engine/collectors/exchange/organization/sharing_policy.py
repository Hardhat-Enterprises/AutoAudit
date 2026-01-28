"""Sharing policy collector.

CIS Microsoft 365 Foundations Benchmark Controls:
    v6.0.0: 1.3.3

Connection Method: Exchange Online PowerShell (via Docker container)
Authentication: Client secret via MSAL -> access token passed to -AccessToken parameter
Required Cmdlets: Get-SharingPolicy
Required Permissions: Exchange.ManageAsApp + Exchange role assignment
"""

from typing import Any

from collectors.powershell_base import BasePowerShellCollector
from collectors.powershell_client import PowerShellClient


class SharingPolicyDataCollector(BasePowerShellCollector):
    """Collects sharing policy settings for CIS compliance evaluation.

    This collector retrieves external calendar sharing settings
    to verify proper sharing restrictions are configured.
    """

    async def collect(self, client: PowerShellClient) -> dict[str, Any]:
        """Collect sharing policy data.

        Returns:
            Dict containing:
            - sharing_policies: List of sharing policies
            - default_policy: The default sharing policy
            - policies_allowing_external: Policies that allow external sharing
        """
        policies = await client.run_cmdlet("ExchangeOnline", "Get-SharingPolicy")

        # Handle None, single policy, or list
        if policies is None:
            policies = []
        elif isinstance(policies, dict):
            policies = [policies]

        # Find default policy
        default_policy = next(
            (p for p in policies if p.get("Default")),
            policies[0] if policies else None
        )

        # Check for policies allowing external sharing
        # Domains field contains sharing rules - if it has entries, sharing is enabled
        policies_allowing_external = []
        for policy in policies:
            domains = policy.get("Domains", [])
            if domains:
                policies_allowing_external.append({
                    "name": policy.get("Name"),
                    "domains": domains,
                    "enabled": policy.get("Enabled"),
                })

        return {
            "sharing_policies": policies,
            "total_policies": len(policies),
            "default_policy": default_policy,
            "policies_allowing_external": policies_allowing_external,
        }
