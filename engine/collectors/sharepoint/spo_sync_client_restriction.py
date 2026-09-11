"""SPO sync client restriction collector.

CIS Microsoft 365 Foundations Benchmark Controls:
    v6.0.0: 7.3.2

Connection Method: SharePoint Online PowerShell (via PowerShell HTTP service)
Required Cmdlets: Get-PnPTenantSyncClientRestriction
Required Permissions: SharePoint.Admin

ARCHITECTURE NOTE (2026-09): this collector originally targeted the SharePoint
REST API. That version was never implemented (collect() raised
NotImplementedError) -- the note below is preserved unchanged from it rather
than silently deleted:

    Connection Method: SharePoint REST API
    Authentication: Client secret via MSAL (access token)

    CAVEAT: Access token authentication has not been fully tested.
        It should work, but needs verification during implementation. Certificate-based
        authentication may be required instead of client secret authentication.

    NOTE: This collector uses SharePoint REST API instead of PowerShell because
    SharePoint Online PowerShell does not support client secret authentication.
    If certificate authentication is adopted in the future, this collector should
    be updated to use the Get-SPOTenantSyncClientRestriction cmdlet instead.

    REST Endpoints: SharePoint Admin API for sync client restrictions

That "PowerShell does not support client secret authentication" claim is out of
date: collectors/sharepoint/pnp/tenant.py already runs Get-PnPTenant through the
PowerShell HTTP service using certificate-based auth, and serves 7.2.2, 7.2.5,
7.2.9, and 7.3.1 successfully. This collector follows that same PnP pattern
instead of the REST path, using Get-PnPTenantSyncClientRestriction -- the
PnP.PowerShell equivalent of the Get-SPOTenantSyncClientRestriction cmdlet the
CIS audit steps reference.
"""

from typing import Any

from collectors.powershell_base import BasePowerShellCollector
from collectors.powershell_client import PowerShellClient


class SpoSyncClientRestrictionDataCollector(BasePowerShellCollector):
    """Collects SPO sync client restrictions for CIS compliance evaluation.

    This collector retrieves OneDrive sync restrictions for unmanaged
    devices to verify proper sync controls are in place.
    """

    async def collect(self, client: PowerShellClient) -> dict[str, Any]:
        """Collect SPO sync client restriction data.

        Returns:
            Dict containing:
            - sync_client_restriction: Full Get-PnPTenantSyncClientRestriction result
            - tenant_restriction_enabled: Whether sync is restricted to specific domains (CIS 7.3.2)
            - allowed_domain_list: AD domain GUIDs allowed to sync (CIS 7.3.2)
        """
        sync_client_restriction = await client.run_cmdlet(
            "SharePointOnline", "Get-PnPTenantSyncClientRestriction"
        )

        return {
            "sync_client_restriction": sync_client_restriction,
            "tenant_restriction_enabled": sync_client_restriction.get(
                "TenantRestrictionEnabled"
            ),
            "allowed_domain_list": sync_client_restriction.get("AllowedDomainList"),
        }
