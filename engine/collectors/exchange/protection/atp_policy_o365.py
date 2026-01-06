"""ATP policy for Office 365 collector.

CIS Microsoft 365 Foundations Benchmark Controls:
    v6.0.0: 2.1.5

Connection Method: Exchange Online PowerShell (via Docker container)
Authentication: Client secret via MSAL -> access token passed to -AccessToken parameter
Required Cmdlets: Get-AtpPolicyForO365
Required Permissions: Exchange.ManageAsApp + Exchange role assignment
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
            - enable_atp_for_spo_teams_odb: Safe Docs for SPO/Teams/OneDrive status
            - enable_safe_docs: Safe Documents status
            - allow_safe_docs_open: Allow Safe Docs open in Protected View
        """
        policy = await client.run_cmdlet("ExchangeOnline", "Get-AtpPolicyForO365")

        return {
            "atp_policy": policy,
            "enable_atp_for_spo_teams_odb": policy.get("EnableATPForSPOTeamsODB"),
            "enable_safe_docs": policy.get("EnableSafeDocs"),
            "allow_safe_docs_open": policy.get("AllowSafeDocsOpen"),
        }
