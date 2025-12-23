"""Label policy collector.

STATUS: PENDING - Requires certificate-based authentication
REASON: Security & Compliance PowerShell (IPPSSession) does not support client
        secret authentication for app-only access. Only certificate-based
        authentication works with Connect-IPPSSession for unattended scenarios.
        See: https://learn.microsoft.com/en-us/powershell/exchange/connect-to-scc-powershell
TO ENABLE: Implement certificate-based auth in PowerShellClient, then move this
           collector back to collectors/compliance/ and register it.

CIS Microsoft 365 Foundations Benchmark Controls:
    v6.0.0: 3.3.1

Connection Method: IPPSSession (Security & Compliance PowerShell via Docker container)
Authentication: Certificate-based auth required (client secret NOT supported)
Required Cmdlets: Get-LabelPolicy
Required Permissions: Exchange.ManageAsApp + Compliance role assignment
"""

from typing import Any

from collectors.powershell_base import BasePowerShellCollector
from collectors.powershell_client import PowerShellClient


class LabelPolicyDataCollector(BasePowerShellCollector):
    """Collects sensitivity label policies for CIS compliance evaluation.

    This collector retrieves sensitivity label publishing policies
    to verify proper information protection is configured.
    """

    async def collect(self, client: PowerShellClient) -> dict[str, Any]:
        """Collect label policy data.

        Returns:
            Dict containing:
            - label_policies: List of sensitivity label policies
            - total_policies: Number of label policies
            - enabled_policies: Policies that are enabled
        """
        policies = await client.run_cmdlet("Compliance", "Get-LabelPolicy")

        # Handle single policy vs list
        if isinstance(policies, dict):
            policies = [policies]

        # Find enabled policies
        enabled_policies = [
            {
                "name": p.get("Name"),
                "labels": p.get("Labels", []),
                "exchange_location": p.get("ExchangeLocation"),
            }
            for p in policies
            if p.get("Enabled")
        ]

        return {
            "label_policies": policies,
            "total_policies": len(policies),
            "enabled_policies": enabled_policies,
        }
