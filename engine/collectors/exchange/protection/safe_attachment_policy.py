"""Safe Attachment policy collector.

CIS Microsoft 365 Foundations Benchmark Controls:
    v6.0.0: 2.1.4

Connection Method: Exchange Online PowerShell (via Docker container)
Authentication: Client secret via MSAL -> access token passed to -AccessToken parameter
Required Cmdlets: Get-SafeAttachmentPolicy
Required Permissions: Exchange.ManageAsApp + Exchange role assignment
"""

from typing import Any

from collectors.powershell_base import BasePowerShellCollector
from collectors.powershell_client import PowerShellClient


class SafeAttachmentPolicyDataCollector(BasePowerShellCollector):
    """Collects Safe Attachments policy for CIS compliance evaluation.

    This collector retrieves Safe Attachments configuration to verify
    attachment scanning protection is properly enabled.
    """

    async def collect(self, client: PowerShellClient) -> dict[str, Any]:
        """Collect Safe Attachment policy data.

        Returns:
            Dict containing:
            - safe_attachment_policies: List of Safe Attachment policies
            - policies_with_protection: Policies with protection enabled
        """
        policies = await client.run_cmdlet("ExchangeOnline", "Get-SafeAttachmentPolicy")

        # Handle None, single policy, or list
        if policies is None:
            policies = []
        elif isinstance(policies, dict):
            policies = [policies]

        # Find policies with protection enabled (Action != "Off")
        policies_with_protection = [
            {
                "name": p.get("Name"),
                "action": p.get("Action"),
                "enable": p.get("Enable"),
                "redirect": p.get("Redirect"),
            }
            for p in policies
            if p.get("Enable") and p.get("Action") != "Off"
        ]

        return {
            "safe_attachment_policies": policies,
            "total_policies": len(policies),
            "policies_with_protection": policies_with_protection,
        }
