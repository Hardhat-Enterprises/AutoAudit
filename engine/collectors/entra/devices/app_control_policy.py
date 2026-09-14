"""Application Control policy collector.

Essential Eight Benchmark Controls:
    E8-AC-1.1: Application Control deployed and enforced on workstations

Connection Method: Microsoft Graph API
Required Scopes: DeviceManagementConfiguration.Read.All
Graph Endpoints:
    /v1.0/deviceManagement/deviceConfigurations                  (legacy AppLocker)
    /v1.0/deviceManagement/deviceConfigurations/{id}/assignments (legacy scope)
    /beta/deviceManagement/configurationPolicies                 (modern App Control)
    /beta/deviceManagement/configurationPolicies/{id}/settings   (modern settings)

Two Intune surfaces can carry application control configuration:

1. The legacy Application control profile, exposed on
   windows10EndpointProtectionConfiguration objects through the
   appLockerApplicationControl property. This is a documented v1.0 enum that
   states the audit or enforce intent directly, so it is the preferred source.
2. Modern App Control for Business policies, which use the ApplicationControl
   CSP and are surfaced through the beta settings-catalog endpoints. These
   expose configured policy intent only.

Microsoft does not document a first-class Graph property for the device-side
effective state of an App Control policy (an IsDeployed or IsEffective flag).
The collector therefore reports effective_device_state_verified as False and
the policy returns insufficient evidence rather than a pass where enforcement
cannot be established from configuration alone.

Research reference: 26T2-SEC-KHS-001, 26T2-SEC-TD-001
"""

from typing import Any

from collectors.base import BaseDataCollector
from collectors.graph_client import GraphClient


# windows10EndpointProtectionConfiguration.appLockerApplicationControl enum,
# lowercased. Anything outside this map normalises to "unknown", which is absent
# from ENFORCING_STATES in the Rego policy, so an unrecognised or future value
# fails closed instead of being read as enforcement.
# Source: https://learn.microsoft.com/en-us/graph/api/intune-deviceconfig-windows10endpointprotectionconfiguration-list
APPLOCKER_STATE_MAP = {
    "notconfigured": "not_configured",
    "enforcecomponentsandstoreapps": "enforced",
    "auditcomponentsandstoreapps": "audit_only",
    "enforcecomponentsstoreappsandsmartlocker": "enforced",
    "auditcomponentsstoreappsandsmartlocker": "audit_only",
}

# Identifies an App Control for Business policy among settings-catalog policies.
APP_CONTROL_TEMPLATE_HINTS = ("app control", "application control")

# Substrings identifying built-in-control settings within a policy's
# settingDefinitionId. Settings-catalog identifiers are verbose and version
# dependent, so they are matched by substring rather than exact value.
SETTING_HINT_TRUST_WINDOWS = "trustwindows"
SETTING_HINT_REPUTATION = "intelligentsecuritygraph"
SETTING_HINT_MANAGED_INSTALLER = "managedinstaller"

LEGACY_ODATA_HINT = "windows10endpointprotectionconfiguration"

# Assignment target types, matched as substrings of the target's @odata.type.
# Source: https://learn.microsoft.com/en-us/graph/api/resources/intune-shared-devicandappmanagementassignmenttarget
TARGET_HINT_ALL_DEVICES = "alldevicesassignmenttarget"
TARGET_HINT_ALL_USERS = "alllicensedusersassignmenttarget"
TARGET_HINT_EXCLUSION = "exclusiongroupassignmenttarget"
TARGET_HINT_GROUP = "groupassignmenttarget"

# Ordering used to select the weakest policy. A policy that reaches nothing is
# weaker than one whose coverage cannot be established, which is in turn weaker
# than one assigned tenant-wide.
ASSIGNMENT_SCOPE_RANK = {
    "all_devices": 0,
    "group_scoped": 1,
    "unknown": 2,
    "none": 3,
}

NO_POLICY_RESULT: dict[str, Any] = {
    "policies_found": 0,
    "weakest_policy_name": None,
    "graph_source_type": None,
    "graph_policy_id": None,
    "configured_enforcement_state": "not_configured",
    "trust_reputation": False,
    "trust_managed_installer": False,
    "assignment_scope": "none",
    "has_exclusions": False,
    "effective_device_state_verified": False,
}


def _normalize_applocker_state(raw: str | None) -> str:
    """Map an appLockerApplicationControl enum value to a canonical state."""
    return APPLOCKER_STATE_MAP.get((raw or "").strip().lower(), "unknown")


def _analyse_assignments(assignments: list[dict[str, Any]]) -> tuple[str, bool]:
    """Classify how widely a policy is deployed.

    The presence of an assignment record is not proof that the workstations in
    scope receive the policy: a profile targeted at a pilot group, or one with
    exclusions applied, reaches only part of the fleet. Returns the assignment
    scope and whether any exclusion target is present, so the policy can report
    insufficient evidence where tenant-wide coverage cannot be established.
    """
    if not assignments:
        return "none", False

    target_types = [
        (a.get("target") or {}).get("@odata.type", "").lower() for a in assignments
    ]
    has_exclusions = any(TARGET_HINT_EXCLUSION in t for t in target_types)

    if any(
        TARGET_HINT_ALL_DEVICES in t or TARGET_HINT_ALL_USERS in t for t in target_types
    ):
        return "all_devices", has_exclusions
    if any(TARGET_HINT_GROUP in t for t in target_types):
        return "group_scoped", has_exclusions
    return "unknown", has_exclusions


def _is_app_control_policy(policy: dict[str, Any]) -> bool:
    """Return True if a settings-catalog policy is an App Control policy."""
    template = policy.get("templateReference") or {}
    display_name = (template.get("templateDisplayName") or "").lower()
    return any(hint in display_name for hint in APP_CONTROL_TEMPLATE_HINTS)


def _setting_value(instance: dict[str, Any]) -> str | None:
    """Extract a comparable scalar from a settings-catalog setting instance."""
    choice = instance.get("choiceSettingValue")
    if isinstance(choice, dict):
        value = choice.get("value")
        if isinstance(value, str):
            # Values arrive as fully qualified ids ending in the option name.
            return value.rsplit("_", 1)[-1]
    simple = instance.get("simpleSettingValue")
    if isinstance(simple, dict):
        value = simple.get("value")
        if value is not None:
            return str(value)
    return None


def _is_enabled(value: str | None) -> bool:
    """Interpret a settings-catalog boolean-ish value."""
    return (value or "").strip().lower() in ("1", "true", "enabled")


class AppControlPolicyDataCollector(BaseDataCollector):
    """Collects Intune application control configuration from both Graph surfaces.

    ASD ML1 requires application control to be implemented on workstations and
    restricted to an organisation-approved set. A policy in audit mode records
    execution without preventing it, so audit-only deployments are reported
    distinctly from enforced ones.

    Where a tenant defines multiple policies, a single unassigned, audit-only or
    reputation-only policy undermines the control, so the weakest policy
    determines the result and is surfaced by name for remediation. This mirrors
    the weakest-state selection used by ASRRulesDataCollector.
    """

    async def collect(self, client: GraphClient) -> dict[str, Any]:
        """Collect application control policy data."""
        findings: list[dict[str, Any]] = []
        findings.extend(await self._collect_legacy(client))
        findings.extend(await self._collect_modern(client))

        if not findings:
            # No Intune policy does not prove unauthorised code can run: the
            # tenant may enforce application control by another mechanism. The
            # Rego policy reports this as insufficient evidence.
            return dict(NO_POLICY_RESULT)

        weakest = max(
            findings,
            key=lambda f: (
                ASSIGNMENT_SCOPE_RANK.get(f["assignment_scope"], 2),
                f["has_exclusions"],
                f["configured_enforcement_state"] != "enforced",
                f["trust_reputation"] and not f["trust_managed_installer"],
            ),
        )
        return {
            "policies_found": len(findings),
            "weakest_policy_name": weakest["policy_name"],
            "graph_source_type": weakest["graph_source_type"],
            "graph_policy_id": weakest["graph_policy_id"],
            "configured_enforcement_state": weakest["configured_enforcement_state"],
            "trust_reputation": weakest["trust_reputation"],
            "trust_managed_installer": weakest["trust_managed_installer"],
            "assignment_scope": weakest["assignment_scope"],
            "has_exclusions": weakest["has_exclusions"],
            # Microsoft exposes no documented Graph property for the device-side
            # effective state of an application control policy, so configuration
            # intent is all that can be established here.
            "effective_device_state_verified": False,
        }

    async def _collect_legacy(self, client: GraphClient) -> list[dict[str, Any]]:
        """Read legacy Application control profiles (AppLocker CSP)."""
        configs = await client.get_all_pages("/deviceManagement/deviceConfigurations")
        findings: list[dict[str, Any]] = []
        for config in configs:
            if LEGACY_ODATA_HINT not in config.get("@odata.type", "").lower():
                continue
            raw_state = config.get("appLockerApplicationControl")
            if raw_state is None:
                continue
            config_id = config.get("id")
            assignments = await client.get_all_pages(
                f"/deviceManagement/deviceConfigurations/{config_id}/assignments"
            )
            scope, has_exclusions = _analyse_assignments(assignments)
            findings.append(
                {
                    "policy_name": config.get("displayName"),
                    "graph_source_type": "legacy_device_configuration",
                    "graph_policy_id": config_id,
                    "configured_enforcement_state": _normalize_applocker_state(
                        raw_state
                    ),
                    # The legacy profile has no reputation or managed installer
                    # options; those exist only on modern App Control policies.
                    "trust_reputation": False,
                    "trust_managed_installer": False,
                    "assignment_scope": scope,
                    "has_exclusions": has_exclusions,
                }
            )
        return findings

    async def _collect_modern(self, client: GraphClient) -> list[dict[str, Any]]:
        """Read modern App Control for Business policies (ApplicationControl CSP)."""
        policies = await client.get_all_pages(
            "/deviceManagement/configurationPolicies", beta=True
        )
        findings: list[dict[str, Any]] = []
        for policy in policies:
            if not _is_app_control_policy(policy):
                continue

            policy_id = policy.get("id")
            settings = await client.get_all_pages(
                f"/deviceManagement/configurationPolicies/{policy_id}/settings",
                beta=True,
            )
            assignments = await client.get_all_pages(
                f"/deviceManagement/configurationPolicies/{policy_id}/assignments",
                beta=True,
            )

            enforcement_raw: str | None = None
            trust_reputation = False
            trust_managed_installer = False

            for setting in settings:
                instance = setting.get("settingInstance") or {}
                definition_id = (instance.get("settingDefinitionId") or "").lower()
                value = _setting_value(instance)
                if SETTING_HINT_TRUST_WINDOWS in definition_id:
                    enforcement_raw = value
                elif SETTING_HINT_REPUTATION in definition_id:
                    trust_reputation = _is_enabled(value)
                elif SETTING_HINT_MANAGED_INSTALLER in definition_id:
                    trust_managed_installer = _is_enabled(value)

            # A policy exposing no readable built-in setting was authored with
            # custom XML, which this collector cannot interpret. It resolves to
            # "unknown" so the control reports insufficient evidence.
            if enforcement_raw is None:
                state = "unknown"
            elif _is_enabled(enforcement_raw):
                state = "enforced"
            elif "audit" in enforcement_raw.strip().lower():
                state = "audit_only"
            else:
                state = "unknown"

            scope, has_exclusions = _analyse_assignments(assignments)
            findings.append(
                {
                    "policy_name": policy.get("name") or policy.get("displayName"),
                    "graph_source_type": "modern_configuration_policy",
                    "graph_policy_id": policy_id,
                    "configured_enforcement_state": state,
                    "trust_reputation": trust_reputation,
                    "trust_managed_installer": trust_managed_installer,
                    "assignment_scope": scope,
                    "has_exclusions": has_exclusions,
                }
            )
        return findings
