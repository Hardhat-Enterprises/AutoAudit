"""Fabric tenant settings collector.

CIS Microsoft 365 Foundations Benchmark Controls:
    v6.0.0: 9.1.1, 9.1.2, 9.1.3, 9.1.4, 9.1.5, 9.1.6, 9.1.7, 9.1.8, 9.1.9, 9.1.10, 9.1.11, 9.1.12

Connection Method: Fabric Admin REST API
Required Scopes: Tenant.Read.All (Fabric API) or Fabric Administrator role
API Endpoint: GET https://api.fabric.microsoft.com/v1/admin/tenantsettings
Rate Limit: 25 requests per minute

CAVEAT: Access token authentication for the Fabric API has not been fully tested.
    It should work using MSAL token acquisition with the Fabric API scope, but this
    needs verification during implementation. Certificate-based authentication may
    be required instead of client secret authentication for some tenant configurations.

Controls covered:
    - 9.1.1: Ensure guest user access is restricted
    - 9.1.2: Ensure external user invitations are restricted
    - 9.1.3: Ensure guest access to content is restricted
    - 9.1.4: Ensure 'Publish to web' is restricted
    - 9.1.5: Ensure 'Interact with and share R and Python' visuals is 'Disabled'
    - 9.1.6: Ensure 'Allow users to apply sensitivity labels for content' is 'Enabled'
    - 9.1.7: Ensure shareable links are restricted
    - 9.1.8: Ensure enabling of external data sharing is restricted
    - 9.1.9: Ensure 'Block ResourceKey Authentication' is 'Enabled'
    - 9.1.10: Ensure access to APIs by service principals is restricted
    - 9.1.11: Ensure service principals cannot create and use profiles
    - 9.1.12: Ensure service principals ability to create workspaces, connections and deployment pipelines is restricted
"""

from typing import Any

from collectors.base import BaseDataCollector
from collectors.graph_client import GraphClient


class FabricTenantSettingsDataCollector(BaseDataCollector):
    """Collects Microsoft Fabric tenant settings for CIS compliance evaluation.

    This collector retrieves all Fabric tenant settings via the Fabric Admin API.
    Note: Requires a separate Fabric API client (not Graph API).
    """

    async def collect(self, client: GraphClient) -> dict[str, Any]:
        """Collect Fabric tenant settings data.

        Returns:
            Dict containing:
            - tenant_settings: List of all tenant settings with their configurations
            - guest_access_restricted: Whether guest user access is restricted
            - external_invitations_restricted: Whether external invitations are restricted
            - publish_to_web_restricted: Whether publish to web is restricted
            - r_python_visuals_disabled: Whether R/Python visuals are disabled
            - sensitivity_labels_enabled: Whether sensitivity labels are enabled
            - shareable_links_restricted: Whether shareable links are restricted
            - external_data_sharing_restricted: Whether external data sharing is restricted
            - resource_key_auth_blocked: Whether ResourceKey authentication is blocked
            - service_principal_api_access_restricted: Whether SP API access is restricted
            - service_principal_profiles_disabled: Whether SP profiles are disabled
            - service_principal_workspace_creation_restricted: Whether SP workspace creation is restricted
        """
        # TODO: Implement collector
        # Note: This requires a Fabric-specific client, not the Graph client
        # Endpoint: GET https://api.fabric.microsoft.com/v1/admin/tenantsettings
        # May need to create FabricClient similar to GraphClient
        raise NotImplementedError("Collector not yet implemented")
