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
    raw_policies: Any = await client.run_cmdlet("ExchangeOnline", "Get-OwaMailboxPolicy")
    raw_org_config: Any = await client.run_cmdlet("ExchangeOnline", "Get-OrganizationConfig")

    policies: list[dict[str, Any]]
    if raw_policies is None:
        policies = []
    elif isinstance(raw_policies, dict):
        policies = [raw_policies]
    else:
        policies = raw_policies

    default_policy = next(
        (p for p in policies if p.get("IsDefault")),
        policies[0] if policies else None
    )
    default_policy_bookings_mailbox_creation_enabled = (
        default_policy.get("BookingsMailboxCreationEnabled")
        if default_policy else None
    )
    policies_with_external_storage = [
        p.get("Name") for p in policies
        if p.get("AdditionalStorageProvidersAvailable")
    ]
    policies_with_bookings = [
        p.get("Name") for p in policies
        if p.get("BookingsMailboxCreationEnabled")
    ]
    bookings_enabled = raw_org_config.get("BookingsEnabled") if raw_org_config else None

    return {
        "owa_policies": policies,
        "total_policies": len(policies),
        "default_policy": default_policy,
        "default_policy_bookings_mailbox_creation_enabled": default_policy_bookings_mailbox_creation_enabled,
        "policies_with_external_storage": policies_with_external_storage,
        "policies_with_bookings": policies_with_bookings,
        "bookings_enabled": bookings_enabled,
    }