"""External access policy collector.

STATUS: PENDING - MicrosoftTeams module AccessTokens auth not working
REASON: Connect-MicrosoftTeams with -AccessTokens parameter returns
        "Not supported tenant type" error. This is a known bug in the
        MicrosoftTeams PowerShell module affecting certain tenant configurations.
        See: https://techcommunity.microsoft.com/discussions/teamsdeveloper/authenticating-with-an-access-token-connect-microsoftteams/2233794
TO ENABLE: Either wait for Microsoft to fix the module, or implement
           certificate-based auth. Then move this collector back to
           collectors/teams/ and register it.

CIS Microsoft 365 Foundations Benchmark Controls:
    v6.0.0: 8.2.1, 8.2.2, 8.2.3

Connection Method: Microsoft Teams PowerShell (via Docker container)
Authentication: AccessTokens auth currently broken - certificate auth may work
Required Cmdlets: Get-CsExternalAccessPolicy
Required Permissions: Teams.ManageAsApp + Teams Admin role
"""

from typing import Any

from collectors.powershell_base import BasePowerShellCollector
from collectors.powershell_client import PowerShellClient


class ExternalAccessPolicyDataCollector(BasePowerShellCollector):
    """Collects external access policy for CIS compliance evaluation.

    This collector retrieves external access settings for Teams
    communication with external organizations.
    """

    async def collect(self, client: PowerShellClient) -> dict[str, Any]:
        """Collect external access policy data.

        Returns:
            Dict containing:
            - external_access_policies: List of external access policies
            - global_policy: The global external access policy
        """
        policies = await client.run_cmdlet("Teams", "Get-CsExternalAccessPolicy")

        # Handle single policy vs list
        if isinstance(policies, dict):
            policies = [policies]

        # Find global policy
        global_policy = next(
            (p for p in policies if p.get("Identity") == "Global"),
            None
        )

        return {
            "external_access_policies": policies,
            "total_policies": len(policies),
            "global_policy": global_policy,
        }
