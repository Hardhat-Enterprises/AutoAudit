"""OWA mailbox policy collector.

CIS Microsoft 365 Foundations Benchmark Controls:
    v6.0.0: 1.3.9, 6.3.1, 6.5.3

Connection Method: Exchange Online PowerShell (via Docker container)
Authentication: Client secret via MSAL -> access token passed to -AccessToken parameter
Required Cmdlets: Get-OwaMailboxPolicy
Required Permissions: Exchange.ManageAsApp + Exchange role assignment
"""

from typing import Any

from collectors.powershell_base import BasePowerShellCollector
from collectors.powershell_client import PowerShellClient


class OwaMailboxPolicyDataCollector(BasePowerShellCollector):
    """Collects OWA mailbox policy settings for CIS compliance evaluation.

    This collector retrieves OWA settings including bookings, add-ins,
    and storage provider configurations.
    """

    async def collect(self, client: PowerShellClient) -> dict[str, Any]:
        """Collect OWA mailbox policy data.

        Returns:
            Dict containing:
            - owa_policies: List of OWA mailbox policies
            - policies_with_external_storage: Policies allowing external storage
            - policies_with_bookings: Policies with Bookings enabled
        """
        policies = await client.run_cmdlet("ExchangeOnline", "Get-OwaMailboxPolicy")

        # Handle None, single policy, or list
        if policies is None:
            policies = []
        elif isinstance(policies, dict):
            policies = [policies]

        # Find default policy
        default_policy = next(
            (p for p in policies if p.get("IsDefault")),
            policies[0] if policies else None
        )

        # Check for policies with external storage enabled
        policies_with_external_storage = [
            p.get("Name") for p in policies
            if p.get("AdditionalStorageProvidersAvailable")
        ]

        # Check for policies with Bookings enabled
        policies_with_bookings = [
            p.get("Name") for p in policies
            if p.get("BookingsMailboxCreationEnabled")
        ]

        return {
            "owa_policies": policies,
            "total_policies": len(policies),
            "default_policy": default_policy,
            "policies_with_external_storage": policies_with_external_storage,
            "policies_with_bookings": policies_with_bookings,
        }
