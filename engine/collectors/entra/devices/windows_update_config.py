"""Windows Update for Business configuration collector.

Essential Eight Benchmark Controls:
    E8-POS-1.1: Operating system patches applied within the required timeframe

Connection Method: Microsoft Graph API
Required Scopes: DeviceManagementConfiguration.Read.All
Graph Endpoints:
    /v1.0/deviceManagement/deviceConfigurations (Windows Update for Business profiles)
"""

from typing import Any

from collectors.base import BaseDataCollector
from collectors.graph_client import GraphClient


# Microsoft Graph windowsUpdateType / automaticUpdateMode enum values, lowercased.
# Source: https://learn.microsoft.com/en-us/graph/api/resources/intune-deviceconfig-windowsupdateforbusinessconfiguration
# Anything not in the map returns "unknown", which is absent from
# ENFORCING_UPDATE_MODES in the Rego policy — so a future Intune enum addition
# fails closed rather than being silently treated as compliant.
INTUNE_UPDATE_MODE_MAP = {
    "userdefined": "user_defined",
    "notifydownload": "notify_download",
    "autoinstallatmaintenancetime": "auto_install",
    "autoinstallandrebootatmaintenancetime": "auto_install_and_reboot",
    "autoinstallandrebootatscheduledtime": "auto_install_and_reboot",
    "autoinstallandrebootwithoutendusercontrol": "auto_install_and_reboot",
    "windowsdefault": "windows_default",
}

NO_PROFILE_RESULT: dict[str, Any] = {
    "profiles_found": 0,
    "weakest_profile_name": None,
    "quality_updates_deferral_days": 0,
    "quality_updates_deadline_days": 0,
    "deadline_grace_period_days": 0,
    "days_to_active": 0,
    "quality_updates_paused": False,
    "automatic_update_mode": "not_configured",
}


def _normalize_mode(raw: str) -> str:
    """Map an Intune automaticUpdateMode enum value to a canonical mode string."""
    return INTUNE_UPDATE_MODE_MAP.get((raw or "").lower(), "unknown")


class WindowsUpdateConfigDataCollector(BaseDataCollector):
    """Collects Windows Update for Business ring configuration from Intune.

    ASD ML1 requires patches to be applied within two weeks on the highest-risk
    system class. Where a tenant defines multiple update rings, a single
    permissive ring undermines the control, so the weakest ring determines the
    result and is surfaced by name for remediation.

    Days to active is the sum of the deferral period, the deadline and the
    grace period, matching Microsoft's own reference ring arithmetic.
    """

    async def collect(self, client: GraphClient) -> dict[str, Any]:
        """Collect Windows Update for Business configuration data."""
        configs = await client.get_all_pages("/deviceManagement/deviceConfigurations")
        findings: list[dict[str, Any]] = []
        for config in configs:
            if "windowsupdateforbusiness" not in config.get("@odata.type", "").lower():
                continue
            deferral = config.get("qualityUpdatesDeferralPeriodInDays") or 0
            deadline = config.get("deadlineForQualityUpdatesInDays") or 0
            grace = config.get("deadlineGracePeriodInDays") or 0
            findings.append(
                {
                    "profile_name": config.get("displayName"),
                    "quality_updates_deferral_days": deferral,
                    "quality_updates_deadline_days": deadline,
                    "deadline_grace_period_days": grace,
                    "days_to_active": deferral + deadline + grace,
                    "quality_updates_paused": bool(config.get("qualityUpdatesPaused")),
                    "automatic_update_mode": _normalize_mode(
                        config.get("automaticUpdateMode")
                    ),
                }
            )

        if not findings:
            # A tenant managed by Windows Autopatch returns no Windows Update for
            # Business profiles despite a sound patching posture. The policy
            # surfaces this as a distinct message requiring manual verification.
            return dict(NO_PROFILE_RESULT)

        # Weakest ring wins: paused first, then non-enforcing update mode, then
        # the longest time to active. Mirrors the ASR collector's weakest-state
        # selection across Endpoint Protection profiles.
        enforcing = {"auto_install", "auto_install_and_reboot"}
        weakest = max(
            findings,
            key=lambda f: (
                f["quality_updates_paused"],
                f["automatic_update_mode"] not in enforcing,
                f["days_to_active"],
            ),
        )
        return {
            "profiles_found": len(findings),
            "weakest_profile_name": weakest["profile_name"],
            "quality_updates_deferral_days": weakest["quality_updates_deferral_days"],
            "quality_updates_deadline_days": weakest["quality_updates_deadline_days"],
            "deadline_grace_period_days": weakest["deadline_grace_period_days"],
            "days_to_active": weakest["days_to_active"],
            "quality_updates_paused": weakest["quality_updates_paused"],
            "automatic_update_mode": weakest["automatic_update_mode"],
        }
