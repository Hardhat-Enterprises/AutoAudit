"""Attack Surface Reduction (ASR) rules collector.

Essential Eight Benchmark Controls:
    E8-MAC-2.1: Macros are blocked from making Win32 API calls
    E8-UAH-2.1: Microsoft Office is blocked from creating child processes

Connection Method: Microsoft Graph API
Required Scopes: DeviceManagementConfiguration.Read.All
Graph Endpoints:
    /v1.0/deviceManagement/deviceConfigurations (legacy Endpoint Protection list)
    /beta/deviceManagement/deviceConfigurations/{id} (legacy detail; v1.0 omits ASR fields)
"""

from typing import Any

from collectors.base import BaseDataCollector
from collectors.graph_client import GraphClient


# Microsoft Graph defenderAttackSurfaceReductionType enum values, lowercased.
# Source: https://learn.microsoft.com/en-us/graph/api/resources/intune-deviceconfig-defenderattacksurfacereductiontype
# Anything not in the map returns "unknown", which the severity comparison
# below treats as weakest — so a future Intune enum addition fails closed in
# the Rego policy rather than being silently misclassified.
INTUNE_ASR_STATE_MAP = {
    "block": "block",
    "audit": "audit",
    "auditmode": "audit",  # Graph literal is "auditMode"
    "warn": "warn",
    "disable": "disabled",
    "userdefined": "disabled",
    "notconfigured": "not_configured",
    "off": "disabled",
}

# ASD ML2 requires Block on every profile. If any profile is weaker, the
# tenant is non-compliant. Order: disabled < audit < warn < block.
_SEVERITY = {
    "unknown": -1,
    "not_configured": 0,
    "disabled": 1,
    "audit": 2,
    "warn": 3,
    "block": 4,
}


def _normalize_state(raw: str) -> str:
    """Map an Intune ASR enum value to block / audit / warn / disabled / not_configured."""
    return INTUNE_ASR_STATE_MAP.get((raw or "").lower(), "unknown")


def _weakest(findings: list[tuple[str, str | None]]) -> dict[str, Any]:
    """Reduce a list of (normalized_state, profile_name) readings for one ASR
    rule down to the single weakest state Essential Eight cares about, plus
    which profile it came from -- shared by every rule this collector reads,
    since ASD's "every profile must enforce Block" requirement is the same
    for each of them."""
    if not findings:
        return {"rule_found": False, "rule_state": "not_configured", "policy_name": None}
    weakest_state, weakest_name = min(findings, key=lambda f: _SEVERITY.get(f[0], -1))
    return {"rule_found": True, "rule_state": weakest_state, "policy_name": weakest_name}


class ASRRulesDataCollector(BaseDataCollector):
    """Collects ASR rule configurations from Intune.

    Reads two Attack Surface Reduction rules off the same legacy Endpoint
    Protection device configurations in a single pass over the tenant's
    profiles (one Graph call per profile either way, so reading a second
    rule here is free):

    - Win32 API calls from Office macros (E8-MAC-2.1):
      `defenderOfficeMacroCodeAllowWin32ImportsType`
    - Office applications creating child processes (E8-UAH-2.1):
      `defenderOfficeAppsLaunchChildProcessType`

    The v1.0 schema for windows10EndpointProtectionConfiguration omits ASR
    rule properties; the beta endpoint exposes both fields above.
    Source: https://learn.microsoft.com/en-us/graph/api/resources/intune-deviceconfig-windows10endpointprotectionconfiguration?view=graph-rest-beta
    """

    async def collect(self, client: GraphClient) -> dict[str, Any]:
        """Collect ASR rule configuration data."""
        configs = await client.get_all_pages("/deviceManagement/deviceConfigurations")

        win32_findings: list[tuple[str, str | None]] = []
        child_process_findings: list[tuple[str, str | None]] = []

        for config in configs:
            if "endpointprotection" not in config.get("@odata.type", "").lower():
                continue
            config_id = config.get("id")
            if not config_id:
                continue
            full_config = await client.get(
                f"/deviceManagement/deviceConfigurations/{config_id}",
                beta=True,
            )
            display_name = config.get("displayName")

            win32_value = full_config.get("defenderOfficeMacroCodeAllowWin32ImportsType")
            if win32_value:
                win32_findings.append((_normalize_state(win32_value), display_name))

            child_process_value = full_config.get("defenderOfficeAppsLaunchChildProcessType")
            if child_process_value:
                child_process_findings.append((_normalize_state(child_process_value), display_name))

        win32 = _weakest(win32_findings)
        child_process = _weakest(child_process_findings)

        return {
            "win32_api_rule_found": win32["rule_found"],
            "win32_api_rule_state": win32["rule_state"],
            "source": "legacy_endpoint_protection" if win32["rule_found"] else None,
            "policy_name": win32["policy_name"],
            "office_child_process_rule_found": child_process["rule_found"],
            "office_child_process_rule_state": child_process["rule_state"],
            "office_child_process_source": (
                "legacy_endpoint_protection" if child_process["rule_found"] else None
            ),
            "office_child_process_policy_name": child_process["policy_name"],
        }
