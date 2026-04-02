"""SPO tenant collector.

CIS Microsoft 365 Foundations Benchmark Controls:
    v6.0.0: 7.2.1, 7.2.3, 7.2.4, 7.2.5, 7.2.6, 7.2.7, 7.2.8, 7.2.9, 7.2.10, 7.2.11, 7.3.1

Connection Method: Microsoft Graph
Authentication: Client secret via MSAL application permissions

Graph Endpoints: GET /admin/sharepoint/settings
"""

from typing import Any

from collectors.base import BaseDataCollector
from collectors.sharepoint_client import SharePointClient


class SpoTenantDataCollector(BaseDataCollector):
    """Collects SPO tenant settings for CIS compliance evaluation.

    This collector retrieves tenant-wide SharePoint settings including
    sharing, authentication, guest access, and other configurations.
    """

    @staticmethod
    def _first_present(data: dict[str, Any], *keys: str) -> Any:
        """Return the first non-missing value from a set of possible keys."""
        for key in keys:
            if key in data:
                return data[key]
        return None

    @staticmethod
    def _as_list(value: Any) -> list[Any]:
        """Normalize SharePoint list-like fields to plain lists."""
        if value is None:
            return []
        if isinstance(value, list):
            return value
        if isinstance(value, tuple):
            return list(value)
        if isinstance(value, str):
            if not value.strip():
                return []
            return [item.strip() for item in value.split(",") if item.strip()]
        if isinstance(value, dict) and isinstance(value.get("results"), list):
            return value["results"]
        return [value]

    @staticmethod
    def _as_bool(value: Any) -> bool | None:
        """Normalize bool-like values from Graph/REST payloads."""
        if value is None:
            return None
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            normalized = value.strip().lower()
            if normalized in {"true", "1", "yes"}:
                return True
            if normalized in {"false", "0", "no"}:
                return False
        return None

    @classmethod
    def _prevent_external_users_from_resharing(cls, tenant_settings: dict[str, Any]) -> bool | None:
        """Resolve guest resharing protection from direct or inverse field variants."""
        direct_value = cls._first_present(
            tenant_settings,
            "PreventExternalUsersFromResharing",
            "preventExternalUsersFromResharing",
        )
        direct_bool = cls._as_bool(direct_value)
        if direct_bool is not None:
            return direct_bool

        inverse_value = cls._first_present(
            tenant_settings,
            "isResharingByExternalUsersEnabled",
            "IsResharingByExternalUsersEnabled",
        )
        inverse_bool = cls._as_bool(inverse_value)
        if inverse_bool is not None:
            return not inverse_bool

        return None

    async def collect(self, client: SharePointClient) -> dict[str, Any]:
        """Collect SPO tenant data.

        Returns:
            Dict containing:
            - tenant_settings: Full tenant configuration
            - legacy_auth_protocols_enabled: Legacy auth status
            - sharing_capability: External sharing capability
            - default_sharing_link_type: Default sharing link type
            - default_link_permission: Default link permission level
        """
        tenant_settings = await client.get_tenant_settings()

        return {
            "tenant_settings": tenant_settings,
            "legacy_auth_protocols_enabled": self._first_present(
                tenant_settings,
                "isLegacyAuthProtocolsEnabled",
                "LegacyAuthProtocolsEnabled",
                "legacyAuthProtocolsEnabled",
            ),
            "sharing_capability": self._first_present(
                tenant_settings,
                "SharingCapability",
                "sharingCapability",
                "CoreSharingCapability",
                "coreSharingCapability",
            ),
            "onedrive_sharing_capability": self._first_present(
                tenant_settings,
                "OneDriveSharingCapability",
                "oneDriveSharingCapability",
            ),
            "default_sharing_link_type": self._first_present(
                tenant_settings,
                "DefaultSharingLinkType",
                "defaultSharingLinkType",
                "CoreDefaultShareLinkScope",
                "coreDefaultShareLinkScope",
            ),
            "default_link_permission": self._first_present(
                tenant_settings,
                "DefaultLinkPermission",
                "defaultLinkPermission",
                "DefaultShareLinkRole",
                "defaultShareLinkRole",
                "CoreDefaultShareLinkRole",
                "coreDefaultShareLinkRole",
            ),
            "prevent_external_users_from_resharing": self._prevent_external_users_from_resharing(
                tenant_settings
            ),
            "sharing_domain_restriction_mode": self._first_present(
                tenant_settings,
                "SharingDomainRestrictionMode",
                "sharingDomainRestrictionMode",
            ),
            "sharing_allowed_domain_list": self._as_list(
                self._first_present(
                    tenant_settings,
                    "SharingAllowedDomainList",
                    "sharingAllowedDomainList",
                )
            ),
            "sharing_blocked_domain_list": self._as_list(
                self._first_present(
                    tenant_settings,
                    "SharingBlockedDomainList",
                    "sharingBlockedDomainList",
                )
            ),
            "restrict_external_sharing": self._as_list(
                self._first_present(
                    tenant_settings,
                    "RestrictExternalSharing",
                    "restrictExternalSharing",
                )
            ),
            "external_user_expiration_required": self._first_present(
                tenant_settings,
                "ExternalUserExpirationRequired",
                "externalUserExpirationRequired",
            ),
            "external_user_expire_in_days": self._first_present(
                tenant_settings,
                "ExternalUserExpireInDays",
                "externalUserExpireInDays",
            ),
            "email_attestation_required": self._first_present(
                tenant_settings,
                "EmailAttestationRequired",
                "emailAttestationRequired",
            ),
            "email_attestation_reauth_days": self._first_present(
                tenant_settings,
                "EmailAttestationReAuthDays",
                "emailAttestationReAuthDays",
            ),
            "disallow_infected_file_download": self._first_present(
                tenant_settings,
                "DisallowInfectedFileDownload",
                "disallowInfectedFileDownload",
            ),
            "core_default_share_link_scope": self._first_present(
                tenant_settings,
                "CoreDefaultShareLinkScope",
                "coreDefaultShareLinkScope",
            ),
            "core_default_share_link_role": self._first_present(
                tenant_settings,
                "CoreDefaultShareLinkRole",
                "coreDefaultShareLinkRole",
            ),
            "onedrive_default_share_link_scope": self._first_present(
                tenant_settings,
                "OneDriveDefaultShareLinkScope",
                "oneDriveDefaultShareLinkScope",
            ),
            "onedrive_default_share_link_role": self._first_present(
                tenant_settings,
                "OneDriveDefaultShareLinkRole",
                "oneDriveDefaultShareLinkRole",
            ),
        }
