"""Fabric tenant settings collector.

CIS Microsoft 365 Foundations Benchmark Controls:
    v6.0.0: 9.1.1, 9.1.2, 9.1.3, 9.1.4, 9.1.5, 9.1.6, 9.1.7, 9.1.8, 9.1.9, 9.1.10, 9.1.11, 9.1.12

Control Descriptions:
    9.1.1 - Ensure guest user access is restricted
    9.1.2 - Ensure external user invitations are restricted
    9.1.3 - Ensure guest access to content is restricted
    9.1.4 - Ensure 'Publish to web' is restricted
    9.1.5 - Ensure 'Interact with and share R and Python' visuals is 'Disabled'
    9.1.6 - Ensure 'Allow users to apply sensitivity labels for content' is 'Enabled'
    9.1.7 - Ensure shareable links are restricted
    9.1.8 - Ensure enabling of external data sharing is restricted
    9.1.9 - Ensure 'Block ResourceKey Authentication' is 'Enabled'
    9.1.10 - Ensure access to APIs by service principals is restricted
    9.1.11 - Ensure service principals cannot create and use profiles
    9.1.12 - Ensure service principals ability to create workspaces is restricted

Connection Method: Fabric Admin REST API
Required Scopes: Tenant.Read.All (Fabric API) or Fabric Administrator role
API Endpoint: GET https://api.fabric.microsoft.com/v1/admin/tenantsettings
Rate Limit: 25 requests per minute

CAVEAT: Access token authentication for the Fabric API has not been fully tested.
    It should work using MSAL token acquisition with the Fabric API scope, but this
    needs verification during implementation. Certificate-based authentication may
    be required instead of client secret authentication for some tenant configurations.
"""

from typing import Any

from collectors.base import BaseDataCollector
from collectors.graph_client import GraphClient


class FabricTenantSettingsDataCollector(BaseDataCollector):
    """Collects Microsoft Fabric tenant settings for CIS compliance evaluation.

    This collector retrieves all Fabric tenant settings via the Fabric Admin API.
    Note: Requires a separate Fabric API client (not Graph API).
    """

    # Mapping of setting names to CIS controls for reference
    CIS_SETTING_MAPPINGS = {
        "AllowGuestUserToAccessSharedContent": "9.1.1",
        "AllowExternalUserInvitations": "9.1.2",
        "AllowGuestLookup": "9.1.3",
        "PublishToWeb": "9.1.4",
        "RScriptVisuals": "9.1.5",
        "AllowSensitivityLabelToSetMIPLabel": "9.1.6",
        "AllowShareableLinksForTheEntireOrganization": "9.1.7",
        "AllowExternalDataSharingReceiverSwitch": "9.1.8",
        "BlockResourceKeyAuthentication": "9.1.9",
        "ServicePrincipalAccess": "9.1.10",
        "AllowServicePrincipalsUseProfilesPreview": "9.1.11",
        "CreateWorkspacesServicePrincipal": "9.1.12",
    }

    async def collect(self, client: GraphClient) -> dict[str, Any]:
        """Collect Fabric tenant settings data.

        Note: Uses FabricClient internally as Fabric API is separate from Graph.
        The GraphClient is used to extract credentials for FabricClient.

        Returns:
            Dict containing:
            - tenant_settings: List of all tenant settings with their configurations
            - settings_by_name: Dict mapping setting names to their full config
            - total_settings: Number of settings returned
        """
        from collectors.fabric_client import FabricClient

        # Create Fabric client using same credentials as Graph client
        fabric_client = FabricClient(
            tenant_id=client.tenant_id,
            client_id=client.client_id,
            client_secret=client.client_secret,
        )

        # Get all tenant settings
        settings = await fabric_client.get_tenant_settings()

        # Build lookup by setting name for convenience
        settings_by_name = {s.get("settingName"): s for s in settings}

        return {
            "tenant_settings": settings,
            "settings_by_name": settings_by_name,
            "total_settings": len(settings),
        }
