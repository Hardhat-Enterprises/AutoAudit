"""Office macro notification settings collector.

Essential Eight Benchmark Controls:
    E8-MAC-1.4 – Users cannot change macro settings

Connection Method:
    Microsoft Graph API

Required Scope:
    DeviceManagementConfiguration.Read.All

Graph Endpoints:
    /beta/deviceManagement/configurationPolicies
    /beta/deviceManagement/configurationPolicies/{id}/settings
"""

from typing import Any

from collectors.base import BaseDataCollector
from collectors.graph_client import GraphClient


MACRO_SETTING_SUFFIX = "_l_vbawarningspolicy"


def _get_application(definition_id: str) -> str:
    """Determine the Office application from the Intune setting definition ID."""
    definition_id = definition_id.lower()

    if "excel16v2" in definition_id:
        return "Excel"
    if "ppt16v2" in definition_id:
        return "PowerPoint"
    if "word16v2" in definition_id:
        return "Word"
    if "access16v2" in definition_id:
        return "Access"
    if "outlk16v2" in definition_id:
        return "Outlook"
    if "project16v2" in definition_id:
        return "Project"
    if "pub16v2" in definition_id:
        return "Publisher"
    if "visio16v2" in definition_id:
        return "Visio"

    return "Unknown"


def _get_policy_state(choice_value: str | None) -> str:
    """Normalize the top-level VBA warning policy state."""
    if not choice_value:
        return "unknown"

    if choice_value.endswith("_1"):
        return "enabled"

    if choice_value.endswith("_0"):
        return "disabled"

    return "unknown"


class MacroNotificationSettingsDataCollector(BaseDataCollector):
    """Collect Office VBA Macro Notification Settings from Intune."""

    async def collect(self, client: GraphClient) -> dict[str, Any]:
        """Collect and normalize Office VBA Macro Notification Settings."""

        policies = await client.get_all_pages(
            "/deviceManagement/configurationPolicies",
            beta=True,
        )

        findings: list[dict[str, Any]] = []

        for policy in policies:
            policy_id = policy.get("id")

            if not policy_id:
                continue

            settings = await client.get_all_pages(
                f"/deviceManagement/configurationPolicies/{policy_id}/settings",
                beta=True,
            )

            for setting in settings:
                instance = setting.get("settingInstance", {})
                definition_id = instance.get("settingDefinitionId", "")

                # Only collect VBA Macro Notification Settings.
                if not definition_id.lower().endswith(MACRO_SETTING_SUFFIX):
                    continue

                choice_setting = instance.get("choiceSettingValue", {})
                choice_value = choice_setting.get("value")

                children = choice_setting.get("children", [])

                child_value = None

                if children:
                    child_choice = children[0].get("choiceSettingValue", {})
                    child_value = child_choice.get("value")

                findings.append(
                    {
                        "application": _get_application(definition_id),
                        "state": _get_policy_state(choice_value),
                        "policy_name": policy.get("name"),
                        "policy_id": policy_id,
                        "setting_definition_id": definition_id,
                        "selected_option": child_value,
                    }
                )

        return {
            "macro_settings_found": len(findings) > 0,
            "settings": findings,
            "source": "intune_settings_catalog",
            "total_policies_checked": len(policies),
        }