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

    # Mapping of CIS control requirements to Fabric setting names
    # These are the setting names returned by the Fabric Admin API
    SETTING_MAPPINGS = {
        # 9.1.1: Ensure guest user access is restricted
        "AllowGuestUserToAccessSharedContent": "guest_access_setting",
        # 9.1.2: Ensure external user invitations are restricted
        "AllowExternalUserInvitations": "external_invitations_setting",
        # 9.1.3: Ensure guest access to content is restricted
        "AllowGuestLookup": "guest_lookup_setting",
        # 9.1.4: Ensure 'Publish to web' is restricted
        "PublishToWeb": "publish_to_web_setting",
        # 9.1.5: Ensure 'Interact with and share R and Python' visuals is 'Disabled'
        "RScriptVisuals": "r_python_visuals_setting",
        # 9.1.6: Ensure 'Allow users to apply sensitivity labels for content' is 'Enabled'
        "AllowSensitivityLabelToSetMIPLabel": "sensitivity_labels_setting",
        # 9.1.7: Ensure shareable links are restricted
        "AllowShareableLinksForTheEntireOrganization": "shareable_links_setting",
        # 9.1.8: Ensure enabling of external data sharing is restricted
        "AllowExternalDataSharingReceiverSwitch": "external_data_sharing_setting",
        # 9.1.9: Ensure 'Block ResourceKey Authentication' is 'Enabled'
        "BlockResourceKeyAuthentication": "resource_key_auth_setting",
        # 9.1.10: Ensure access to APIs by service principals is restricted
        "ServicePrincipalAccess": "sp_api_access_setting",
        # 9.1.11: Ensure service principals cannot create and use profiles
        "AllowServicePrincipalsUseProfilesPreview": "sp_profiles_setting",
        # 9.1.12: Ensure service principals ability to create workspaces is restricted
        "CreateWorkspacesServicePrincipal": "sp_workspace_creation_setting",
    }

    async def collect(self, client: GraphClient) -> dict[str, Any]:
        """Collect Fabric tenant settings data.

        Note: Uses FabricClient internally as Fabric API is separate from Graph.
        The GraphClient is used to extract credentials for FabricClient.

        Returns:
            Dict containing:
            - tenant_settings: List of all tenant settings with their configurations
            - settings_by_name: Dict mapping setting names to their full config
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
        from collectors.fabric_client import FabricClient

        # Create Fabric client using same credentials as Graph client
        fabric_client = FabricClient(
            tenant_id=client.tenant_id,
            client_id=client.client_id,
            client_secret=client.client_secret,
        )

        # Get all tenant settings
        settings = await fabric_client.get_tenant_settings()

        # Build lookup by setting name
        settings_by_name = {s.get("settingName"): s for s in settings}

        # Helper to check if a setting is restricted (disabled or limited to specific groups)
        def is_restricted(setting_name: str) -> bool | None:
            """Check if a setting is restricted (disabled or limited to groups)."""
            setting = settings_by_name.get(setting_name)
            if setting is None:
                return None
            # Setting is restricted if disabled OR if only enabled for specific security groups
            enabled = setting.get("enabled", False)
            has_security_groups = bool(setting.get("enabledSecurityGroups", []))
            # Restricted means: disabled, or enabled only for specific groups (not entire org)
            return not enabled or has_security_groups

        def is_enabled(setting_name: str) -> bool | None:
            """Check if a setting is enabled."""
            setting = settings_by_name.get(setting_name)
            if setting is None:
                return None
            return setting.get("enabled", False)

        def is_disabled(setting_name: str) -> bool | None:
            """Check if a setting is disabled."""
            setting = settings_by_name.get(setting_name)
            if setting is None:
                return None
            return not setting.get("enabled", True)

        return {
            "tenant_settings": settings,
            "total_settings": len(settings),
            "settings_by_name": settings_by_name,
            # CIS control-specific assessments
            # 9.1.1: Guest access should be restricted (disabled or limited)
            "guest_access_restricted": is_restricted("AllowGuestUserToAccessSharedContent"),
            "guest_access_setting": settings_by_name.get("AllowGuestUserToAccessSharedContent"),
            # 9.1.2: External invitations should be restricted
            "external_invitations_restricted": is_restricted("AllowExternalUserInvitations"),
            "external_invitations_setting": settings_by_name.get("AllowExternalUserInvitations"),
            # 9.1.3: Guest lookup should be restricted
            "guest_lookup_restricted": is_restricted("AllowGuestLookup"),
            "guest_lookup_setting": settings_by_name.get("AllowGuestLookup"),
            # 9.1.4: Publish to web should be restricted
            "publish_to_web_restricted": is_restricted("PublishToWeb"),
            "publish_to_web_setting": settings_by_name.get("PublishToWeb"),
            # 9.1.5: R/Python visuals should be disabled
            "r_python_visuals_disabled": is_disabled("RScriptVisuals"),
            "r_python_visuals_setting": settings_by_name.get("RScriptVisuals"),
            # 9.1.6: Sensitivity labels should be enabled
            "sensitivity_labels_enabled": is_enabled("AllowSensitivityLabelToSetMIPLabel"),
            "sensitivity_labels_setting": settings_by_name.get("AllowSensitivityLabelToSetMIPLabel"),
            # 9.1.7: Shareable links should be restricted
            "shareable_links_restricted": is_restricted("AllowShareableLinksForTheEntireOrganization"),
            "shareable_links_setting": settings_by_name.get("AllowShareableLinksForTheEntireOrganization"),
            # 9.1.8: External data sharing should be restricted
            "external_data_sharing_restricted": is_restricted("AllowExternalDataSharingReceiverSwitch"),
            "external_data_sharing_setting": settings_by_name.get("AllowExternalDataSharingReceiverSwitch"),
            # 9.1.9: Resource key auth should be blocked (setting enabled = blocked)
            "resource_key_auth_blocked": is_enabled("BlockResourceKeyAuthentication"),
            "resource_key_auth_setting": settings_by_name.get("BlockResourceKeyAuthentication"),
            # 9.1.10: Service principal API access should be restricted
            "service_principal_api_access_restricted": is_restricted("ServicePrincipalAccess"),
            "service_principal_api_access_setting": settings_by_name.get("ServicePrincipalAccess"),
            # 9.1.11: Service principal profiles should be disabled
            "service_principal_profiles_disabled": is_disabled("AllowServicePrincipalsUseProfilesPreview"),
            "service_principal_profiles_setting": settings_by_name.get("AllowServicePrincipalsUseProfilesPreview"),
            # 9.1.12: Service principal workspace creation should be restricted
            "service_principal_workspace_creation_restricted": is_restricted("CreateWorkspacesServicePrincipal"),
            "service_principal_workspace_creation_setting": settings_by_name.get("CreateWorkspacesServicePrincipal"),
        }
