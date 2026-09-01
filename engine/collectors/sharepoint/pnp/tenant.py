"""PnP SharePoint tenant collector.

CIS Microsoft 365 Foundations Benchmark Controls:
    v6.0.0: 7.3.1

Control Descriptions:
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

    This collector retrieves tenant-wide SharePoint settings. CIS 7.3.1
    evaluates DisallowInfectedFileDownload; later controls can reuse the
    same tenant evidence.
    """

    async def collect(self, client: PowerShellClient) -> dict[str, Any]:
        """Collect SharePoint tenant data.

        Returns:
            Dict containing:
            - tenant: Full Get-PnPTenant result
            - disallow_infected_file_download: Infected-file download status (CIS 7.3.1)
        """
        tenant = await client.run_cmdlet("SharePointOnline", "Get-PnPTenant")

        return {
            "tenant": tenant,
            "disallow_infected_file_download": tenant.get(
                "DisallowInfectedFileDownload"
            ),
            "prevent_external_users_from_resharing": tenant.get(
                "PreventExternalUsersFromResharing"
            ),
        }
