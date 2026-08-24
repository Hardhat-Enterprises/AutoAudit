"""OWA mailbox policy collector.

CIS Microsoft 365 Foundations Benchmark Controls:
    v6.0.0: 1.3.9, 6.3.1, 6.5.3

Connection Method: Exchange Online PowerShell (via Docker container)
Authentication: Client secret via MSAL -> access token passed to -AccessToken parameter
Required Cmdlets: Get-OwaMailboxPolicy, Get-OrganizationConfig
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
        raw_policies: Any = await client.run_cmdlet("ExchangeOnline", "Get-OwaMailboxPolicy")

        # Handle None, single policy, or list
        policies: list[dict[str, Any]]
        if raw_policies is None:
            policies = []
        elif isinstance(raw_policies, dict):
            policies = [raw_policies]
        else:
            policies = raw_policies

        # Find default policy
        default_policy = next(
            (p for p in policies if p.get("IsDefault")),
            policies[0] if policies else None
        )
        # Find default policy for Booking
        default_policy_bookings_mailbox_creation_enabled = (
            default_policy.get("BookingsMailboxCreationEnabled")
            if default_policy
            else None
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

        # CIS 1.3.9 also allows an org-level compliant state: Bookings disabled
        # tenant-wide (Get-OrganizationConfig -> BookingsEnabled)
        org_config = await client.run_cmdlet("ExchangeOnline", "Get-OrganizationConfig")

        return {
            "owa_policies": policies,
            "total_policies": len(policies),
            "default_policy": default_policy,
            "default_policy_bookings_mailbox_creation_enabled": default_policy_bookings_mailbox_creation_enabled,
            "policies_with_external_storage": policies_with_external_storage,
            "policies_with_bookings": policies_with_bookings,
            "bookings_enabled": org_config.get("BookingsEnabled") if org_config else None,
        }
