"""Teams messaging policy collector.

STATUS: PENDING - MicrosoftTeams module AccessTokens auth not working
REASON: Connect-MicrosoftTeams with -AccessTokens parameter returns
        "Not supported tenant type" error. This is a known bug in the
        MicrosoftTeams PowerShell module affecting certain tenant configurations.
        See: https://techcommunity.microsoft.com/discussions/teamsdeveloper/authenticating-with-an-access-token-connect-microsoftteams/2233794
TO ENABLE: Either wait for Microsoft to fix the module, or implement
           certificate-based auth. Then move this collector back to
           collectors/teams/ and register it.

CIS Microsoft 365 Foundations Benchmark Controls:
    v6.0.0: 8.6.1

Connection Method: Microsoft Teams PowerShell (via Docker container)
Authentication: AccessTokens auth currently broken - certificate auth may work
Required Cmdlets: Get-CsTeamsMessagingPolicy
Required Permissions: Teams.ManageAsApp + Teams Admin role
"""

from typing import Any

from collectors.powershell_base import BasePowerShellCollector
from collectors.powershell_client import PowerShellClient


class TeamsMessagingPolicyDataCollector(BasePowerShellCollector):
    """Collects Teams messaging policies for CIS compliance evaluation.

    This collector retrieves messaging settings including user reporting
    for security concerns.
    """

    async def collect(self, client: PowerShellClient) -> dict[str, Any]:
        """Collect Teams messaging policy data.

        Returns:
            Dict containing:
            - messaging_policies: List of messaging policies
            - global_policy: The global messaging policy
            - allow_security_end_user_reporting: User security reporting status
        """
        policies = await client.run_cmdlet("Teams", "Get-CsTeamsMessagingPolicy")

        # Handle single policy vs list
        if isinstance(policies, dict):
            policies = [policies]

        # Find global policy
        global_policy = next(
            (p for p in policies if p.get("Identity") == "Global"),
            None
        )

        return {
            "messaging_policies": policies,
            "total_policies": len(policies),
            "global_policy": global_policy,
            "allow_security_end_user_reporting": global_policy.get("AllowSecurityEndUserReporting") if global_policy else None,
        }
