"""PnP SharePoint tenant collector.

CIS Microsoft 365 Foundations Benchmark Controls:
    v6.0.0: 7.2.1, 7.3.1

Control Descriptions:
    7.2.1 - Ensure modern authentication for SharePoint applications is required
    7.3.1 - Ensure Office 365 SharePoint infected files are disallowed for download

Connection Method: SharePoint Online PowerShell (via PowerShell HTTP service)
Required Cmdlets: Get-PnPTenant
Required Permissions: SharePoint.Admin
"""

from typing import Any

from collectors.powershell_base import BasePowerShellCollector
from collectors.powershell_client import PowerShellClient


class PnpTenantDataCollector(BasePowerShellCollector):
    """Collects SharePoint tenant settings via Get-PnPTenant.

    This collector retrieves tenant-wide SharePoint settings. CIS 7.2.1
    evaluates LegacyAuthProtocolsEnabled; CIS 7.3.1 evaluates
    DisallowInfectedFileDownload. Later controls can reuse the same
    tenant evidence.
    """

    async def collect(self, client: PowerShellClient) -> dict[str, Any]:
        """Collect SharePoint tenant data.

        Returns:
            Dict containing:
            - tenant: Full Get-PnPTenant result
            - legacy_auth_protocols_enabled: Legacy auth protocol status (CIS 7.2.1)
            - disallow_infected_file_download: Infected-file download status (CIS 7.3.1)
        """
        tenant = await client.run_cmdlet("SharePointOnline", "Get-PnPTenant")

        return {
            "tenant": tenant,
            "legacy_auth_protocols_enabled": tenant.get(
                "LegacyAuthProtocolsEnabled"
            ),
            "disallow_infected_file_download": tenant.get(
                "DisallowInfectedFileDownload"
            ),
        }