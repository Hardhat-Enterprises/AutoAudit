"""SPO tenant collector.

CIS Microsoft 365 Foundations Benchmark Controls:
    v6.0.0: 7.2.1, 7.2.2, 7.2.3, 7.2.4, 7.2.5, 7.2.6, 7.2.7, 7.2.9, 7.2.10, 7.2.11, 7.3.1

Connection Method: SharePoint REST API
Authentication: Client secret via MSAL (access token)

CAVEAT: Access token authentication has not been fully tested.
    It should work, but needs verification during implementation. Certificate-based
    authentication may be required instead of client secret authentication.

NOTE: This collector uses SharePoint REST API instead of PowerShell because
SharePoint Online PowerShell does not support client secret authentication.
If certificate authentication is adopted in the future, this collector should
be updated to use the Get-SPOTenant cmdlet instead.

REST Endpoints: /_api/SPOTenant or SharePoint Admin API
"""

from typing import Any

from collectors.base import BaseDataCollector
from collectors.sharepoint_client import SharePointClient


class SpoTenantDataCollector(BaseDataCollector):
    """Collects SPO tenant settings for CIS compliance evaluation.

    This collector retrieves tenant-wide SharePoint settings including
    sharing, authentication, guest access, and other configurations.
    """

    async def collect(self, client: SharePointClient) -> dict[str, Any]:
        """Collect SPO tenant data.

        Returns:
            Dict containing:
            - tenant_settings: Full tenant configuration
            - legacy_auth_protocols_enabled: Legacy auth status
            - azure_ad_b2b_integration_enabled: B2B integration status
            - sharing_capability: External sharing capability
            - default_sharing_link_type: Default sharing link type
            - default_link_permission: Default link permission level
        """
        settings = await client.get_tenant_settings()

        # Map a handful of frequently used fields to make OPA policy writing easier
        legacy_auth_enabled = settings.get("LegacyAuthProtocolsEnabled")
        sharing_capability = settings.get("SharingCapability")
        default_link_type = settings.get("DefaultSharingLinkType")
        default_link_permission = settings.get("DefaultLinkPermission")
        guest_expiration_days = settings.get("ExternalUserExpirationInDays")
        conditional_access_policy = settings.get("ConditionalAccessPolicy")
        limited_access_file_type = settings.get("LimitedAccessFileType")

        return {
            "tenant_settings": settings,
            "legacy_auth_protocols_enabled": legacy_auth_enabled,
            "sharing_capability": sharing_capability,
            "default_sharing_link_type": default_link_type,
            "default_link_permission": default_link_permission,
            "guest_expiration_days": guest_expiration_days,
            "conditional_access_policy": conditional_access_policy,
            "limited_access_file_type": limited_access_file_type,
        }
