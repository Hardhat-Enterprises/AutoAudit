"""ATP policy for Office 365 collector.

CIS Microsoft 365 Foundations Benchmark Controls:
    v6.0.0: 2.1.5

Connection Method: Exchange Online PowerShell
Authentication: Client secret via MSAL -> access token passed to -AccessToken parameter
Required Cmdlets: Get-AtpPolicyForO365

CAVEAT: Access token authentication (-AccessToken) has not been fully tested.
    It should work, but needs verification during implementation. Certificate-based
    authentication may be required instead of client secret authentication.
"""

from typing import Any

from collectors.powershell_base import BasePowerShellCollector
from collectors.powershell_client import PowerShellClient


class AtpPolicyO365DataCollector(BasePowerShellCollector):
    """Collects ATP policy for O365 for CIS compliance evaluation.

    This collector retrieves Safe Attachments settings for SharePoint,
    OneDrive, and Teams to verify protection is enabled.
    """

    async def collect(self, client: PowerShellClient) -> dict[str, Any]:
        """Collect ATP policy for O365 data.

        Returns:
            Dict containing:
            - atp_policy: The ATP policy for Office 365
            - sharepoint_enabled: Safe Attachments for SharePoint status
            - onedrive_enabled: Safe Attachments for OneDrive status
            - teams_enabled: Safe Attachments for Teams status
        """
        # TODO: Implement collector
        raise NotImplementedError("Collector not yet implemented")
