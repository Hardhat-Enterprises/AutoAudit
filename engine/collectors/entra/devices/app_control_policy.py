"""App Control for Business policy collector.

Essential Eight Benchmark Controls:
    E8-AC-1.1: Application Control deployed and enforced on workstations

Connection Method: Microsoft Graph API
Required Scopes: DeviceManagementConfiguration.Read.All
Graph Endpoints:
    /v1.0/deviceManagement/configurationPolicies              (policy list)
    /v1.0/deviceManagement/configurationPolicies/{id}/settings    (setting values)
    /v1.0/deviceManagement/configurationPolicies/{id}/assignments (deployment)

Intune App Control for Business policies use the Windows ApplicationControl CSP
and are surfaced through the settings-catalog `configurationPolicies` endpoint,
not `deviceConfigurations`. The older Application control profiles under Attack
Surface Reduction use the AppLocker CSP and are documented by Microsoft as
pending deprecation, so they are deliberately out of scope here.

Research reference: 26T2-SEC-KHS-001, 26T2-SEC-TD-001
"""

from typing import Any

from collectors.base import BaseDataCollector
from collectors.graph_client import GraphClient


# Identifies an App Control for Business policy among all settings-catalog
# policies. Matched case-insensitively against the template display name.
APP_CONTROL_TEMPLATE_HINTS = ("app control", "application control")

# Base PolicyIDs assigned by Intune to policies built with the "built-in
# controls" format. Used as a fallback when the template reference is absent.
# Source: https://learn.microsoft.com/en-us/intune/device-configuration/endpoint-security/manage-app-control
BUILT_IN_BASE_POLICY_IDS = {
    "{a8012cfc-d8ae-493c-b2ea-510f035f1250}",
    "{d6d6c2d6-e8b6-4d8f-8223-14be1de562ff}",
    "{63d1178a-816a-4ab6-8ecd-127f2df0ce47}",
    "{2da0f72d-1688-4097-847d-c42c39e631bc}",
}

# Substrings identifying the built-in-control settings within a policy's
# settingDefinitionId. Settings-catalog identifiers are verbose and version
# dependent, so they are matched by substring rather than exact value.
SETTING_HINT_TRUST_WINDOWS = "trustwindows"
SETTING_HINT_REPUTATION = "intelligentsecuritygraph"
SETTING_HINT_MANAGED_INSTALLER = "managedinstaller"

# Enforcement states derived from the "Enable trust of Windows components and
# store apps" setting. Anything unrecognised normalises to "unknown", which is
# absent from ENFORCING_MODES in the Rego policy, so a future Intune value
# fails closed rather than silently passing.
ENFORCEMENT_MODE_MAP = {
    "enabled": "enforced",
    "true": "enforced",
    "1": "enforced",
    "audit": "audit_only",
    "auditonly": "audit_only",
    "audit only": "audit_only",
    "2": "audit_only",
    "notconfigured": "not_configured",
    "disabled": "not_configured",
    "0": "not_configured",
}

NO_POLICY_RESULT: dict[str, Any] = {
    "policies_found": 0,
    "weakest_policy_name": None,
    "policy_format": "none",
    "enforcement_mode": "not_configured",
    "trust_reputation": False,
    "trust_managed_installer": False,
    "assigned": False,
}


def _normalize_enforcement(raw: str | None) -> str:
    """Map an App Control trust setting value to a canonical enforcement mode."""
    key = (raw or "").strip().lower().replace("_", "")
    return ENFORCEMENT_MODE_MAP.get(key, "unknown")


def _is_app_control_policy(policy: dict[str, Any]) -> bool:
    """Return True if a settings-catalog policy is an App Control policy."""
    template = policy.get("templateReference") or {}
    display_name = (template.get("templateDisplayName") or "").lower()
    if any(hint in display_name for hint in APP_CONTROL_TEMPLATE_HINTS):
        return True
    template_id = (template.get("templateId") or "").lower()
    return template_id in BUILT_IN_BASE_POLICY_IDS


def _setting_value(instance: dict[str, Any]) -> str | None:
    """Extract a comparable scalar from a settings-catalog setting instance.

    Settings-catalog instances nest their value differently depending on the
    setting type. Only the shapes App Control uses are handled; anything else
    returns None and is treated as unrecognised by the caller.
    """
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


class AppControlPolicyDataCollector(BaseDataCollector):
    """Collects Intune App Control for Business policy configuration.

    ASD ML1 requires application control to be implemented on workstations and
    restricted to an organisation-approved set. A policy that exists but runs in
    audit mode permits every application to execute, so audit-only deployments
    are reported distinctly from enforced ones.

    Where a tenant defines multiple App Control policies, a single audit-only or
    reputation-only policy undermines the control, so the weakest policy
    determines the result and is surfaced by name for remediation. This mirrors
    the weakest-state selection used by ASRRulesDataCollector.
    """

    async def collect(self, client: GraphClient) -> dict[str, Any]:
        """Collect App Control for Business policy data."""
        policies = await client.get_all_pages("/deviceManagement/configurationPolicies")
        findings: list[dict[str, Any]] = []

        for policy in policies:
            if not _is_app_control_policy(policy):
                continue

            policy_id = policy.get("id")
            settings = await client.get_all_pages(
                f"/deviceManagement/configurationPolicies/{policy_id}/settings"
            )
            assignments = await client.get_all_pages(
                f"/deviceManagement/configurationPolicies/{policy_id}/assignments"
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
                    trust_reputation = str(value).lower() in ("1", "true", "enabled")
                elif SETTING_HINT_MANAGED_INSTALLER in definition_id:
                    trust_managed_installer = str(value).lower() in (
                        "1",
                        "true",
                        "enabled",
                    )

            findings.append(
                {
                    "policy_name": policy.get("name") or policy.get("displayName"),
                    # A policy carrying no readable built-in settings was authored
                    # with custom XML, which this collector cannot interpret.
                    "policy_format": "built_in" if enforcement_raw else "xml",
                    "enforcement_mode": _normalize_enforcement(enforcement_raw),
                    "trust_reputation": trust_reputation,
                    "trust_managed_installer": trust_managed_installer,
                    "assigned": len(assignments) > 0,
                }
            )

        if not findings:
            # No App Control policy does not by itself prove unauthorised code can
            # run: the tenant may enforce application control outside Intune. The
            # policy surfaces this as requiring manual verification.
            return dict(NO_POLICY_RESULT)

        # Weakest policy wins: unassigned first, then non-enforcing mode, then
        # reputation-only trust, which the Essential Eight does not accept as an
        # organisation-approved set.
        weakest = max(
            findings,
            key=lambda f: (
                not f["assigned"],
                f["enforcement_mode"] != "enforced",
                f["trust_reputation"] and not f["trust_managed_installer"],
            ),
        )
        return {
            "policies_found": len(findings),
            "weakest_policy_name": weakest["policy_name"],
            "policy_format": weakest["policy_format"],
            "enforcement_mode": weakest["enforcement_mode"],
            "trust_reputation": weakest["trust_reputation"],
            "trust_managed_installer": weakest["trust_managed_installer"],
            "assigned": weakest["assigned"],
        }
