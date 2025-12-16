"""External in Outlook collector.

CIS Microsoft 365 Foundations Benchmark Controls:
    v6.0.0: 6.2.3

Connection Method: Exchange Online PowerShell
Authentication: Client secret via MSAL -> access token passed to -AccessToken parameter
Required Cmdlets: Get-ExternalInOutlook
"""

from typing import Any

from collectors.powershell_base import BasePowerShellCollector
from collectors.powershell_client import PowerShellClient


class ExternalInOutlookDataCollector(BasePowerShellCollector):
    """Collects external sender tagging settings for CIS compliance evaluation.

    This collector retrieves external sender identification settings
    to verify external senders are properly tagged in Outlook.
    """

    async def collect(self, client: PowerShellClient) -> dict[str, Any]:
        """Collect external in Outlook data.

        Returns:
            Dict containing:
            - external_in_outlook_settings: External sender tagging config
            - enabled: Whether external tagging is enabled
            - allowed_senders: Senders exempt from tagging
        """
        # TODO: Implement collector
        raise NotImplementedError("Collector not yet implemented")
