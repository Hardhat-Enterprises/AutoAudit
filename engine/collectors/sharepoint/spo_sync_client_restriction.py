"""SPO sync client restriction collector.

CIS Microsoft 365 Foundations Benchmark Controls:
    v6.0.0: 7.3.2

Connection Method: Microsoft Graph
Authentication: Client secret via MSAL application permissions

Graph Endpoints: GET /admin/sharepoint/settings
"""

from typing import Any

from collectors.base import BaseDataCollector
from collectors.sharepoint_client import SharePointClient


class SpoSyncClientRestrictionDataCollector(BaseDataCollector):
    """Collects SPO sync client restrictions for CIS compliance evaluation.

    This collector retrieves OneDrive sync restrictions for unmanaged
    devices to verify proper sync controls are in place.
    """

    async def collect(self, client: SharePointClient) -> dict[str, Any]:
        """Collect SPO sync client restriction data.

        Returns:
            Dict containing:
            - sync_client_restrictions: Sync restriction settings
            - block_mac_sync: Whether Mac sync is blocked for unmanaged
            - domain_guids_allowed: Allowed domain GUIDs for sync
            - excluded_file_extensions: File types excluded from sync
        """
        restrictions = await client.get_sync_client_restriction()

        return {
            "sync_client_restrictions": restrictions,
            "tenant_restriction_enabled": restrictions.get("TenantRestrictionEnabled"),
            "block_mac_sync": restrictions.get("BlockMacSync"),
            "domain_guids_allowed": restrictions.get("AllowedDomainList", []),
            "excluded_file_extensions": restrictions.get("ExcludedFileExtensions", []),
            "groove_block_option": restrictions.get("GrooveBlockOption"),
        }
