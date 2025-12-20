"""DLP compliance policy collector.

STATUS: PENDING - Requires certificate-based authentication
REASON: Security & Compliance PowerShell (IPPSSession) does not support client
        secret authentication for app-only access. Only certificate-based
        authentication works with Connect-IPPSSession for unattended scenarios.
        See: https://learn.microsoft.com/en-us/powershell/exchange/connect-to-scc-powershell
TO ENABLE: Implement certificate-based auth in PowerShellClient, then move this
           collector back to collectors/compliance/ and register it.

CIS Microsoft 365 Foundations Benchmark Controls:
    v6.0.0: 3.2.1, 3.2.2

Connection Method: IPPSSession (Security & Compliance PowerShell via Docker container)
Authentication: Certificate-based auth required (client secret NOT supported)
Required Cmdlets: Get-DlpCompliancePolicy
Required Permissions: Exchange.ManageAsApp + Compliance role assignment
"""

from typing import Any

from collectors.powershell_base import BasePowerShellCollector
from collectors.powershell_client import PowerShellClient


class DlpCompliancePolicyDataCollector(BasePowerShellCollector):
    """Collects DLP compliance policies for CIS compliance evaluation.

    This collector retrieves DLP policies including those covering
    Teams locations for data loss prevention compliance.
    """

    async def collect(self, client: PowerShellClient) -> dict[str, Any]:
        """Collect DLP compliance policy data.

        Returns:
            Dict containing:
            - dlp_policies: List of DLP compliance policies
            - total_policies: Number of DLP policies
            - teams_dlp_policies: Policies covering Teams locations
        """
        policies = await client.run_cmdlet("Compliance", "Get-DlpCompliancePolicy")

        # Handle single policy vs list
        if isinstance(policies, dict):
            policies = [policies]

        # Find policies that cover Teams
        teams_policies = [
            {
                "name": p.get("Name"),
                "mode": p.get("Mode"),
                "enabled": p.get("Enabled"),
                "teams_location": p.get("TeamsLocation"),
            }
            for p in policies
            if p.get("TeamsLocation")
        ]

        return {
            "dlp_policies": policies,
            "total_policies": len(policies),
            "teams_dlp_policies": teams_policies,
        }
