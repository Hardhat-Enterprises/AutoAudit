"""Role assignment policy collector.

CIS Microsoft 365 Foundations Benchmark Controls:
    v6.0.0: 6.3.1

Connection Method: Exchange Online PowerShell (via Docker container)
Authentication: Client secret via MSAL -> access token passed to -AccessToken parameter
Required Cmdlets: Get-RoleAssignmentPolicy
Required Permissions: Exchange.ManageAsApp + Exchange role assignment
"""

from typing import Any

from collectors.powershell_base import BasePowerShellCollector
from collectors.powershell_client import PowerShellClient


class RoleAssignmentPolicyDataCollector(BasePowerShellCollector):
    """Collects role assignment policy for CIS compliance evaluation.

    This collector retrieves Outlook add-in installation permissions
    configured in role assignment policies.
    """

    async def collect(self, client: PowerShellClient) -> dict[str, Any]:
        """Collect role assignment policy data.

        Returns:
            Dict containing:
            - role_assignment_policies: List of role assignment policies
            - default_policy: The default role assignment policy
            - policies_allowing_addin_install: Policies that allow add-in installation
        """
        policies = await client.run_cmdlet("ExchangeOnline", "Get-RoleAssignmentPolicy")

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

        # Check which policies allow add-in installation
        # The assigned roles contain entries like "My Custom Apps", "My Marketplace Apps", "My ReadWriteMailbox Apps"
        policies_allowing_addins = []
        for policy in policies:
            assigned_roles = policy.get("AssignedRoles", [])
            # Check for add-in related roles
            addin_roles = [r for r in assigned_roles if "Apps" in r or "Add-In" in r]
            if addin_roles:
                policies_allowing_addins.append({
                    "name": policy.get("Name"),
                    "is_default": policy.get("IsDefault"),
                    "addin_roles": addin_roles,
                })

        return {
            "role_assignment_policies": policies,
            "total_policies": len(policies),
            "default_policy": default_policy,
            "policies_allowing_addin_install": policies_allowing_addins,
        }
