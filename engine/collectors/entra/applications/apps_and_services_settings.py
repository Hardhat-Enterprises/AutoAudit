"""Apps and services settings collector.

CIS Microsoft 365 Foundations Benchmark Controls:
    v6.0.0: 1.3.4

Connection Method: Microsoft Graph API
Required Scopes: OrgSettings-AppsAndServices.Read.All
Graph Endpoint: /admin/appsAndServices (beta)
"""

from typing import Any

from collectors.base import BaseDataCollector
from collectors.graph_client import GraphClient


class AppsAndServicesSettingsDataCollector(BaseDataCollector):
    """Collects apps and services settings for CIS compliance evaluation.

    This collector retrieves user-owned apps and services settings
    to verify proper application governance configuration.
    """

    async def collect(self, client: GraphClient) -> dict[str, Any]:
        """Collect apps and services settings data.

        Returns:
            Dict containing:
            - apps_and_services_settings: Apps and services configuration
            - is_office_store_enabled: Whether users can access the Office Store
            - is_app_and_services_trial_enabled: Whether users can start trials
            - user_owned_apps_enabled: Back-compat derived signal (best-effort)
        """
        # Prefer the documented Apps & Services admin settings endpoint.
        # Keep a fallback to the older path for compatibility with older tenants.
        collector_error: str | None = None
        try:
            resp = await client.get("/admin/appsAndServices", beta=True)
            raw_settings: dict[str, Any] | None = None

            # Handle a few plausible response shapes defensively.
            if isinstance(resp, dict):
                if isinstance(resp.get("settings"), dict):
                    raw_settings = resp.get("settings")
                else:
                    value = resp.get("value")
                    if isinstance(value, dict) and isinstance(value.get("settings"), dict):
                        raw_settings = value.get("settings")
                    elif isinstance(value, list) and value and isinstance(value[0], dict):
                        if isinstance(value[0].get("settings"), dict):
                            raw_settings = value[0].get("settings")

            settings = raw_settings if raw_settings is not None else (resp or {})
        except Exception as exc:
            collector_error = str(exc)
            try:
                settings = await client.get("/admin/microsoft365Apps/settings", beta=True)
            except Exception as exc2:
                collector_error = f"{collector_error} | fallback_error={exc2}"
                settings = {}

        office_store_enabled = (
            settings.get("isOfficeStoreEnabled") if isinstance(settings, dict) else None
        )
        trial_enabled = (
            settings.get("isAppAndServicesTrialEnabled") if isinstance(settings, dict) else None
        )

        # Best-effort derived signal used by the old policy implementation.
        derived_user_owned_apps_enabled: bool | None
        if isinstance(settings, dict) and "isUserAppsAndServicesEnabled" in settings:
            derived_user_owned_apps_enabled = settings.get("isUserAppsAndServicesEnabled")
        elif office_store_enabled is False and trial_enabled is False:
            derived_user_owned_apps_enabled = False
        elif office_store_enabled is True or trial_enabled is True:
            derived_user_owned_apps_enabled = True
        else:
            derived_user_owned_apps_enabled = None

        return {
            "apps_and_services_settings": settings,
            "is_office_store_enabled": office_store_enabled,
            "is_app_and_services_trial_enabled": trial_enabled,
            "user_owned_apps_enabled": derived_user_owned_apps_enabled,
            "collector_error": collector_error,
        }
