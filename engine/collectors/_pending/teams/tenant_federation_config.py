"""Tenant federation configuration collector.

STATUS: PENDING - MicrosoftTeams module AccessTokens auth not working
REASON: Connect-MicrosoftTeams with -AccessTokens parameter returns
        "Not supported tenant type" error. This is a known bug in the
        MicrosoftTeams PowerShell module affecting certain tenant configurations.
        See: https://techcommunity.microsoft.com/discussions/teamsdeveloper/authenticating-with-an-access-token-connect-microsoftteams/2233794
TO ENABLE: Either wait for Microsoft to fix the module, or implement
           certificate-based auth. Then move this collector back to
           collectors/teams/ and register it.

CIS Microsoft 365 Foundations Benchmark Controls:
    v6.0.0: 8.2.1, 8.2.2, 8.2.3, 8.2.4

Connection Method: Microsoft Teams PowerShell (via Docker container)
Authentication: AccessTokens auth currently broken - certificate auth may work
Required Cmdlets: Get-CsTenantFederationConfiguration
Required Permissions: Teams.ManageAsApp + Teams Admin role
"""

from typing import Any

from collectors.powershell_base import BasePowerShellCollector
from collectors.powershell_client import PowerShellClient


class TenantFederationConfigDataCollector(BasePowerShellCollector):
    """Collects tenant federation configuration for CIS compliance evaluation.

    This collector retrieves federation settings including unmanaged users
    and trial tenant communication settings.
    """

    async def collect(self, client: PowerShellClient) -> dict[str, Any]:
        """Collect tenant federation configuration data.

        Returns:
            Dict containing:
            - federation_config: Full federation configuration
            - allow_federated_users: Federated user access status
            - allow_public_users: Public (Skype) user access status
            - allow_teams_consumer: Teams consumer access status
            - allowed_domains: Allowed federation domains
            - blocked_domains: Blocked federation domains
        """
        config = await client.run_cmdlet("Teams", "Get-CsTenantFederationConfiguration")

        return {
            "federation_config": config,
            "allow_federated_users": config.get("AllowFederatedUsers") if config else None,
            "allow_public_users": config.get("AllowPublicUsers") if config else None,
            "allow_teams_consumer": config.get("AllowTeamsConsumer") if config else None,
            "allow_teams_consumer_inbound": config.get("AllowTeamsConsumerInbound") if config else None,
            "allowed_domains": config.get("AllowedDomains") if config else None,
            "blocked_domains": config.get("BlockedDomains") if config else None,
        }
