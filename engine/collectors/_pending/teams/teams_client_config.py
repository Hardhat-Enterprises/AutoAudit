"""Teams client configuration collector.

STATUS: PENDING - MicrosoftTeams module AccessTokens auth not working
REASON: Connect-MicrosoftTeams with -AccessTokens parameter returns
        "Not supported tenant type" error. This is a known bug in the
        MicrosoftTeams PowerShell module affecting certain tenant configurations.
        See: https://techcommunity.microsoft.com/discussions/teamsdeveloper/authenticating-with-an-access-token-connect-microsoftteams/2233794
TO ENABLE: Either wait for Microsoft to fix the module, or implement
           certificate-based auth. Then move this collector back to
           collectors/teams/ and register it.

CIS Microsoft 365 Foundations Benchmark Controls:
    v6.0.0: 8.1.1, 8.1.2

Connection Method: Microsoft Teams PowerShell (via Docker container)
Authentication: AccessTokens auth currently broken - certificate auth may work
Required Cmdlets: Get-CsTeamsClientConfiguration
Required Permissions: Teams.ManageAsApp + Teams Admin role
"""

from typing import Any

from collectors.powershell_base import BasePowerShellCollector
from collectors.powershell_client import PowerShellClient


class TeamsClientConfigDataCollector(BasePowerShellCollector):
    """Collects Teams client configuration for CIS compliance evaluation.

    This collector retrieves Teams client settings including external
    storage providers and email to channel configurations.
    """

    async def collect(self, client: PowerShellClient) -> dict[str, Any]:
        """Collect Teams client configuration data.

        Returns:
            Dict containing:
            - teams_client_config: Full client configuration
            - allow_dropbox: Dropbox integration status
            - allow_box: Box integration status
            - allow_google_drive: Google Drive integration status
            - allow_sharefile: ShareFile integration status
            - allow_email_into_channel: Email to channel status
        """
        config = await client.run_cmdlet("Teams", "Get-CsTeamsClientConfiguration")

        return {
            "teams_client_config": config,
            "allow_dropbox": config.get("AllowDropBox") if config else None,
            "allow_box": config.get("AllowBox") if config else None,
            "allow_google_drive": config.get("AllowGoogleDrive") if config else None,
            "allow_sharefile": config.get("AllowShareFile") if config else None,
            "allow_email_into_channel": config.get("AllowEmailIntoChannel") if config else None,
        }
