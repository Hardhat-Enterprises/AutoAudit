"""Forms settings collector.

CIS Microsoft 365 Foundations Benchmark Controls:
    v6.0.0: 1.3.5

Connection Method: Microsoft Graph API
Required Scopes: OrgSettings-Forms.Read.All
Graph Endpoint: /admin/forms/settings
"""

from typing import Any

from collectors.base import BaseDataCollector
from collectors.graph_client import GraphClient


class FormsSettingsDataCollector(BaseDataCollector):
    """Collects Microsoft Forms settings for CIS compliance evaluation.

    This collector retrieves Microsoft Forms configuration including
    phishing protection settings for compliance evaluation.
    """

    async def collect(self, client: GraphClient) -> dict[str, Any]:
        """Collect Forms settings data.

        Returns:
            Dict containing:
            - forms_settings: Microsoft Forms configuration
            - internal_phishing_protection_enabled: Phishing protection status
            - external_sharing_enabled: External sharing status
        """
        # Get Microsoft Forms admin settings
        collector_error: str | None = None
        resp: dict[str, Any] = {}
        entry: dict[str, Any] | None = None
        try:
            resp = await client.get("/admin/forms/settings", beta=True)
            raw_settings: dict[str, Any] | None = None

            # Handle a few plausible response shapes defensively.
            if isinstance(resp, dict):
                if isinstance(resp.get("settings"), dict):
                    raw_settings = resp.get("settings")
                elif isinstance(resp.get("formsSettings"), dict):
                    raw_settings = resp.get("formsSettings")
                else:
                    value = resp.get("value")
                    if isinstance(value, dict):
                        entry = value
                        if isinstance(value.get("settings"), dict):
                            raw_settings = value.get("settings")
                        elif isinstance(value.get("formsSettings"), dict):
                            raw_settings = value.get("formsSettings")
                        else:
                            raw_settings = value
                    elif isinstance(value, list) and value and isinstance(value[0], dict):
                        entry = value[0]
                        if isinstance(entry.get("settings"), dict):
                            raw_settings = entry.get("settings")
                        elif isinstance(entry.get("formsSettings"), dict):
                            raw_settings = entry.get("formsSettings")
                        else:
                            raw_settings = entry

            settings = raw_settings if raw_settings is not None else (resp or {})
        except Exception as exc:
            collector_error = str(exc)
            settings = {}

        def _get_setting_value(*keys: str) -> Any:
            for source in (settings, entry, resp):
                if isinstance(source, dict):
                    for key in keys:
                        if key in source:
                            return source.get(key)
            return None

        def _normalize_bool(value: Any) -> bool | None:
            if isinstance(value, bool):
                return value
            if isinstance(value, str):
                normalized = value.strip().lower()
                if normalized in {"on", "enabled", "true", "yes"}:
                    return True
                if normalized in {"off", "disabled", "false", "no"}:
                    return False
            return None

        internal_phishing_protection_enabled = _normalize_bool(
            _get_setting_value(
                "isInternalPhishingProtectionEnabled",
                "internalPhishingProtectionEnabled",
                "isInOrgFormsPhishingScanEnabled",
                "inOrgFormsPhishingScanEnabled",
                "FormsPhishingProtection",
                "formsPhishingProtection",
                "phishingProtection",
            )
        )

        return {
            "forms_settings": settings,
            "internal_phishing_protection_enabled": internal_phishing_protection_enabled,
            "external_sharing_enabled": _normalize_bool(
                _get_setting_value("isExternalSharingEnabled", "externalSharingEnabled")
            ),
            "external_send_form_enabled": _normalize_bool(
                _get_setting_value("isExternalSendFormEnabled", "externalSendFormEnabled")
            ),
            "external_share_collaborating_enabled": _normalize_bool(
                _get_setting_value(
                    "isExternalShareCollaborationEnabled",
                    "isExternalShareCollaboratingEnabled",
                    "externalShareCollaboratingEnabled",
                )
            ),
            "external_share_template_enabled": _normalize_bool(
                _get_setting_value(
                    "isExternalShareTemplateEnabled",
                    "externalShareTemplateEnabled",
                )
            ),
            "external_share_result_enabled": _normalize_bool(
                _get_setting_value(
                    "isExternalShareResultEnabled",
                    "externalShareResultEnabled",
                )
            ),
            "bing_search_enabled": _normalize_bool(
                _get_setting_value(
                    "isBingSearchEnabled",
                    "bingSearchEnabled",
                    "isBingImageSearchEnabled",
                )
            ),
            "record_identity_by_default_enabled": _normalize_bool(
                _get_setting_value(
                    "isRecordIdentityByDefaultEnabled",
                    "recordIdentityByDefaultEnabled",
                )
            ),
            "collector_error": collector_error,
        }
