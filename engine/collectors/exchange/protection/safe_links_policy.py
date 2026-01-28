"""Safe Links policy collector.

CIS Microsoft 365 Foundations Benchmark Controls:
    v6.0.0: 2.1.1

Connection Method: Exchange Online PowerShell (via Docker container)
Authentication: Client secret via MSAL -> access token passed to -AccessToken parameter
Required Cmdlets: Get-SafeLinksPolicy
Required Permissions: Exchange.ManageAsApp + Exchange role assignment
"""

from typing import Any

from collectors.powershell_base import BasePowerShellCollector
from collectors.powershell_client import PowerShellClient


class SafeLinksPolicyDataCollector(BasePowerShellCollector):
    """Collects Safe Links policy for CIS compliance evaluation.

    This collector retrieves Safe Links configuration for Office
    applications to verify URL protection is properly enabled.
    """

    async def collect(self, client: PowerShellClient) -> dict[str, Any]:
        """Collect Safe Links policy data.

        Returns:
            Dict containing:
            - safe_links_policies: List of Safe Links policies
            - policies_with_protection: Policies with URL protection enabled
        """
        policies = await client.run_cmdlet("ExchangeOnline", "Get-SafeLinksPolicy")

        # Handle None, single policy, or list
        if policies is None:
            policies = []
        elif isinstance(policies, dict):
            policies = [policies]

        # Find policies with protection enabled
        policies_with_protection = [
            {
                "name": p.get("Name"),
                "enable_safe_links_for_email": p.get("EnableSafeLinksForEmail"),
                "enable_safe_links_for_office": p.get("EnableSafeLinksForOffice"),
                "enable_safe_links_for_teams": p.get("EnableSafeLinksForTeams"),
                "scan_urls": p.get("ScanUrls"),
                "track_clicks": p.get("TrackClicks"),
            }
            for p in policies
            if p.get("EnableSafeLinksForEmail") or p.get("EnableSafeLinksForOffice")
        ]

        return {
            "safe_links_policies": policies,
            "total_policies": len(policies),
            "policies_with_protection": policies_with_protection,
        }
