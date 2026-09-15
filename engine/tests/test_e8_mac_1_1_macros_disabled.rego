package essential_eight.asd_essential_eight.v2025.test_e8_mac_1_1

import rego.v1

control := data.essential_eight.asd_essential_eight.v2025.control_e8_mac_1_1

# The child settingDefinitionId differs per app (l_empty19 / l_empty4 / l_empty3
# in the live tenant); only the child's value suffix is reliable.

app_prefix := {
	"word": "user_vendor_msft_policy_config_word16v2~policy~l_microsoftofficeword~l_wordoptions~l_security~l_trustcenter_l_vbawarningspolicy",
	"excel": "user_vendor_msft_policy_config_excel16v2~policy~l_microsoftofficeexcel~l_exceloptions~l_security~l_trustcenter_l_vbawarningspolicy",
	"ppt": "user_vendor_msft_policy_config_ppt16v2~policy~l_microsoftofficepowerpoint~l_powerpointoptions~l_security~l_trustcenter_l_vbawarningspolicy",
}

app_child := {"word": "l_empty19", "excel": "l_empty4", "ppt": "l_empty3"}

vba_setting(app, level) := {"settingInstance": {
	"settingDefinitionId": app_prefix[app],
	"choiceSettingValue": {
		"value": sprintf("%s_1", [app_prefix[app]]),
		"children": [{
			"settingDefinitionId": sprintf("%s_%s", [app_prefix[app], app_child[app]]),
			"choiceSettingValue": {
				"value": sprintf("%s_%s_%s", [app_prefix[app], app_child[app], level]),
				"children": [],
			},
		}],
	},
}}

vba_setting_policy_disabled(app, level) := {"settingInstance": {
	"settingDefinitionId": app_prefix[app],
	"choiceSettingValue": {
		"value": sprintf("%s_0", [app_prefix[app]]),
		"children": [{"choiceSettingValue": {"value": sprintf("%s_%s_%s", [app_prefix[app], app_child[app], level])}}],
	},
}}

vba_setting_no_children(app) := {"settingInstance": {
	"settingDefinitionId": app_prefix[app],
	"choiceSettingValue": {
		"value": sprintf("%s_1", [app_prefix[app]]),
		"children": [],
	},
}}

internet_block_setting := {"settingInstance": {
	"settingDefinitionId": "user_vendor_msft_policy_config_word16v2~policy~l_microsoftofficeword~l_wordoptions~l_security~l_trustcenter_l_blockmacroexecutionfrominternet",
	"choiceSettingValue": {
		"value": "user_vendor_msft_policy_config_word16v2~policy~l_microsoftofficeword~l_wordoptions~l_security~l_trustcenter_l_blockmacroexecutionfrominternet_1",
		"children": [],
	},
}}

# A Graph assignment object, trimmed to the parts the policy reads. The policy
# only counts them, so the target shape does not matter here - but it does matter
# that "assigned to nobody" is an empty list, which is what the collector
# normalises a missing key to.
group_assignment := {
	"id": "b1f0c0de-0000-4000-8000-000000000001",
	"source": "direct",
	"target": {
		"@odata.type": "#microsoft.graph.groupAssignmentTarget",
		"groupId": "8f9a0b1c-0000-4000-8000-000000000002",
	},
}

collector_output(settings) := {
	"configuration_policies": [{
		"id": "3e6c6222-4466-401a-8b8d-5c7058c8d432",
		"name": "E8_MACRO",
		"assignments": [group_assignment],
		"settings": settings,
	}],
	"total_configuration_policies": 1,
}

# Same policy, assigned to nobody: the setting is configured correctly but no
# device ever receives it.
collector_output_unassigned(settings) := {
	"configuration_policies": [{
		"id": "3e6c6222-4466-401a-8b8d-5c7058c8d432",
		"name": "E8_MACRO",
		"assignments": [],
		"settings": settings,
	}],
	"total_configuration_policies": 1,
}

# Matches the live MSFT sandbox tenant: all three apps at level 2.
test_compliant_all_apps_disable_with_notification if {
	result := control.result with input as collector_output([
		vba_setting("word", "2"),
		vba_setting("excel", "2"),
		vba_setting("ppt", "2"),
	])

	result.compliant == true
	count(result.details.apps_not_configured) == 0
	count(result.details.apps_misconfigured) == 0
	contains(result.message, "disabled by default")
}

test_compliant_mixed_levels_2_and_4 if {
	result := control.result with input as collector_output([
		vba_setting("word", "4"),
		vba_setting("excel", "2"),
		vba_setting("ppt", "4"),
	])

	result.compliant == true
}

# ML3 hardening (level 3 = signed macros only) must not fail the ML1 control.
test_compliant_level_3_signed_only_satisfies_ml1 if {
	result := control.result with input as collector_output([
		vba_setting("word", "3"),
		vba_setting("excel", "3"),
		vba_setting("ppt", "3"),
	])

	result.compliant == true
}

test_compliant_across_multiple_policies if {
	result := control.result with input as {
		"configuration_policies": [
			{"id": "p1", "name": "Macro baseline - Office", "assignments": [group_assignment], "settings": [vba_setting("word", "2"), vba_setting("excel", "2")]},
			{"id": "p2", "name": "Macro baseline - PowerPoint", "assignments": [group_assignment], "settings": [vba_setting("ppt", "4")]},
		],
		"total_configuration_policies": 2,
	}

	result.compliant == true
	result.details.vba_settings_found == 3
}

test_non_compliant_only_excel_configured if {
	result := control.result with input as collector_output([vba_setting("excel", "2")])

	result.compliant == false
	result.details.compliant_apps == ["Excel"]
	result.details.apps_not_configured == ["PowerPoint", "Word"]
	contains(result.message, "Not configured: PowerPoint, Word")
}

# Level 1 = "Enable all macros" the exact false pass a top level only check gives.
test_non_compliant_level_1_enables_all_macros if {
	result := control.result with input as collector_output([
		vba_setting("word", "1"),
		vba_setting("excel", "1"),
		vba_setting("ppt", "1"),
	])

	result.compliant == false
	result.details.apps_misconfigured == ["Excel", "PowerPoint", "Word"]
	count(result.details.apps_not_configured) == 0
}

test_non_compliant_policy_switched_off if {
	result := control.result with input as collector_output([
		vba_setting_policy_disabled("word", "2"),
		vba_setting_policy_disabled("excel", "2"),
		vba_setting_policy_disabled("ppt", "2"),
	])

	result.compliant == false
	result.details.apps_misconfigured == ["Excel", "PowerPoint", "Word"]
}

test_non_compliant_enabled_but_level_never_selected if {
	result := control.result with input as collector_output([
		vba_setting_no_children("word"),
		vba_setting_no_children("excel"),
		vba_setting_no_children("ppt"),
	])

	result.compliant == false
	some evidence in result.details.settings_evidence
	evidence.level == "unset"
}

test_non_compliant_one_app_at_bad_level if {
	result := control.result with input as collector_output([
		vba_setting("word", "2"),
		vba_setting("excel", "2"),
		vba_setting("ppt", "1"),
	])

	result.compliant == false
	result.details.apps_misconfigured == ["PowerPoint"]
	count(result.details.apps_not_configured) == 0
}

test_non_compliant_no_vba_setting_present if {
	result := control.result with input as collector_output([internet_block_setting])

	result.compliant == false
	result.details.vba_settings_found == 0
	result.details.apps_not_configured == ["Excel", "PowerPoint", "Word"]
}

test_non_compliant_no_configuration_policies if {
	result := control.result with input as {"configuration_policies": [], "total_configuration_policies": 0}

	result.compliant == false
	result.details.total_configuration_policies == 0
}

test_missing_collector_output_returns_default if {
	result := control.result with input as {}

	result.compliant == false
	contains(result.message, "Unable to evaluate")
	count(result.details) == 0
}

# The debug harness wrapper is not the shape the policy receives at scan time.
test_harness_wrapped_input_is_not_accepted if {
	result := control.result with input as {"data": collector_output([
		vba_setting("word", "2"),
		vba_setting("excel", "2"),
		vba_setting("ppt", "2"),
	])}

	contains(result.message, "Unable to evaluate")
}

test_result_details_structure if {
	result := control.result with input as collector_output([
		vba_setting("word", "2"),
		vba_setting("excel", "4"),
		vba_setting("ppt", "2"),
	])

	_ = result.details.total_configuration_policies
	_ = result.details.vba_settings_found
	_ = result.details.compliant_apps
	_ = result.details.apps_not_configured
	_ = result.details.apps_misconfigured
	_ = result.details.settings_evidence

	some evidence in result.details.settings_evidence
	evidence.policy_name == "E8_MACRO"
	evidence.policy_enabled == true
	evidence.app in {"word", "excel", "ppt"}
}

# --- Assignment coverage -----------------------------------------------------

# All three apps configured at a compliant
# level, but the policy is assigned to nobody, so no device receives it.
test_non_compliant_correct_level_but_policy_unassigned if {
	result := control.result with input as collector_output_unassigned([
		vba_setting("word", "2"),
		vba_setting("excel", "2"),
		vba_setting("ppt", "2"),
	])

	result.compliant == false
	result.details.apps_unassigned == ["Excel", "PowerPoint", "Word"]
	result.details.compliant_apps == []
}

# An assignment on a policy carrying the wrong level must not rescue it.
test_non_compliant_assigned_but_wrong_level if {
	result := control.result with input as collector_output([
		vba_setting("word", "1"),
		vba_setting("excel", "1"),
		vba_setting("ppt", "1"),
	])

	result.compliant == false
	count(result.details.apps_unassigned) == 0
}

# Assignments live on the policy, not the setting, so one app can be covered by
# an assigned policy while another sits in an unassigned one.
test_non_compliant_one_app_in_an_unassigned_policy if {
	result := control.result with input as {
		"configuration_policies": [
			{
				"id": "p1", "name": "Assigned baseline",
				"assignments": [group_assignment],
				"settings": [vba_setting("word", "2"), vba_setting("excel", "2")],
			},
			{
				"id": "p2", "name": "Draft, never assigned",
				"assignments": [],
				"settings": [vba_setting("ppt", "2")],
			},
		],
		"total_configuration_policies": 2,
	}

	result.compliant == false
	result.details.compliant_apps == ["Excel", "Word"]
	result.details.apps_unassigned == ["PowerPoint"]
}

# A missing assignments key is treated as unassigned, never as unknown-so-pass.
test_non_compliant_when_assignments_key_is_absent if {
	result := control.result with input as {
		"configuration_policies": [{
			"id": "p1", "name": "E8_MACRO",
			"settings": [vba_setting("word", "2"), vba_setting("excel", "2"), vba_setting("ppt", "2")],
		}],
		"total_configuration_policies": 1,
	}

	result.compliant == false
}
