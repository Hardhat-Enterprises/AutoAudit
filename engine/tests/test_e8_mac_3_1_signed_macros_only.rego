package essential_eight.asd_essential_eight.v2025.test_28_mac_3_1

import rego.v1

control := data.essential_eight.asd_essential_eight.v2025.control_e8_mac_3_1

# Same per-app ID quirk as E8-MAC-1.1's tests
# The child settingDefinitionId suffix differs per app in the live tenant,
# so only the value suffix matters.
app_prefix := {
	"word": "user_vendor_msft_policy_config_word16v2~policy~l_microsoftofficeword~l_wordoptions~l_security~l_trustcenter_l_vbawarningspolicy",
	"excel": "user_vendor_msft_policy_config_excel16v2~policy~l_microsoftofficeexcel~l_exceloptions~l_security~l_trustcenter_l_vbawarningspolicy",
	"ppt": "user_vendor_msft_policy_config_ppt16v2~policy~l_microsoftofficepowerpoint~l_powerpointoptions~l_security~l_trustcenter_l_vbawarningspolicy",
}

app_child := {"word": "1_empty19", "excel": "1_empty4", "ppt": "1_empty3"}

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

# Trimmed graph assignment
# Shape doesn't matter to the policy, only the count.
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

# Same policy, assigned to nobody
# correct value, zero devices reached.
collector_output_unassigned(settings) := {
	"configuration_policies": [{
		"id": "3e6c6222-4466-401a-8b8d-5c7058c8d432",
		"name": "E8_MACRO",
		"assignments": [],
		"settings": settings,
	}],
	"total_configuration_policies": 1,
}


# --Compliant Cases--

test_compliant_all_apps_signed_only if {
	result := control.result with input as collector_output([
		vba_setting("word", "3"),
		vba_setting("excel", "3"),
		vba_setting("ppt", "3"),
	])

	result.compliant == true
	count(result.details.apps_not_configured) == 0
	count(result.details.apps_misconfigured) == 0
	contains(result.message, "digitally signed")
}

test_compliant_across_multiple_policies if {
	result := control.result with input as {
		"configuration_policies": [
			{"id": "p1", "name": "Macro baseline - Office", "assignments": [group_assignment], "settings": [vba_setting("word", "3"), vba_setting("excel", "3")]},
			{"id": "p2", "name": "Macro baseline - PowerPoint", "assignments": [group_assignment], "settings": [vba_setting("ppt", "3")]},
		],
		"total_configuration_policies": 2,
	}

	result.compliant == true
	result.details.vba_settings_found == 3
}


# ---Wrong level cases---
# ML1 control doesn't check this

# Level 2: Satisfies ML1 baseline but not signed only macros = must fail
test_non_compliant_level_2_disable_with_notification if {
	result := control.result with input as collector_output([
		vba_setting("word", "2"),
		vba_setting("excel", "2"),
		vba_setting("ppt", "2"),
	])

	result.compliant == false
	result.details.apps_misconfigured == ["Excel", "PowerPoint", "Word"]
}

# Level 4: Disable without notification = fail
test_non_compliant_level_4_disable_without_notification if {
	result := control.result with input as collector_output([
		vba_setting("word", "4"),
		vba_setting("excel", "4"),
		vba_setting("ppt", "4"),
	])

	result.compliant == false
	result.details.apps_misconfigured == ["Excel", "PowerPoint", "Word"]
}

test_non_compliant_level_1_enables_all_macros if {
	result := control.result with input as collector_output([
		vba_setting("word", "1"),
		vba_setting("excel", "1"),
		vba_setting("ppt", "1"),
	])

	result.compliant == false
	result.details.apps_misconfigured == ["Excel", "PowerPoint", "Word"]
}

test_non_compliant_one_app_at_bad_level if {
	result := control.result with input as collector_output([
		vba_setting("word", "3"),
		vba_setting("excel", "3"),
		vba_setting("ppt", "2"),
	])

	result.compliant == false
	result.details.apps_misconfigured == ["PowerPoint"]
	count(result.details.apps_not_configured) == 0
}

test_non_compliant_only_excel_configured if {
	result := control.result with input as collector_output([vba_setting("excel", "3")])

	result.compliant == false
	result.details.compliant_apps == ["Excel"]
	result.details.apps_not_configured == ["PowerPoint", "Word"]
}

test_non_compliant_policy_switched_off if {
	result := control.result with input as collector_output([
		vba_setting_policy_disabled("word", "3"),
		vba_setting_policy_disabled("excel", "3"),
		vba_setting_policy_disabled("ppt", "3"),
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


# ----Assignment Coverage----

test_non_compliant_correct_level_but_policy_unassigned if {
	result := control.result with input as collector_output_unassigned([
		vba_setting("word", "3"),
		vba_setting("excel", "3"),
		vba_setting("ppt", "3"),
	])

	result.compliant == false
	result.details.apps_unassigned == ["Excel", "PowerPoint", "Word"]
	result.details.compliant_apps == []
}

test_non_compliant_assigned_but_wrong_level if {
	result := control.result with input as collector_output([
		vba_setting("word", "2"),
		vba_setting("excel", "2"),
		vba_setting("ppt", "2"),
	])

	result.compliant == false
	count(result.details.apps_unassigned) == 0
}

test_non_compliant_one_app_in_an_unassigned_policy if {
	result := control.result with input as {
		"configuration_policies": [
			{
				"id": "p1", "name": "Assigned baseline",
				"assignments": [group_assignment],
				"settings": [vba_setting("word", "3"), vba_setting("excel", "3")],
			},
			{
				"id": "p2", "name": "Draft, never assigned",
				"assignments": [],
				"settings": [vba_setting("ppt", "3")],
			},
		],
		"total_configuration_policies": 2,
	}

	result.compliant == false
	result.details.compliant_apps == ["Excel", "Word"]
	result.details.apps_unassigned == ["PowerPoint"]
}

test_non_compliant_when_assignments_key_is_absent if {
	result := control.result with input as {
		"configuration_policies": [{
			"id": "p1", "name": "E8_MACRO",
			"settings": [vba_setting("word", "3"), vba_setting("excel", "3"), vba_setting("ppt", "3")],
		}],
		"total_configuration_policies": 1,
	}

	result.compliant == false
}


# -----Malformed Input-----

test_missing_collector_output_returns_default if {
	result := control.result with input as {}

	result.compliant == false
	contains(result.message, "Unable to evaluate")
	count(result.details) == 0
}

# The debug harness wraps output in "data"; that's not the shape at scan time.
test_harness_wrapped_input_is_not_accepted if {
	result := control.result with input as {"data": collector_output([
		vba_setting("word", "3"),
		vba_setting("excel", "3"),
		vba_setting("ppt", "3"),
	])}

	contains(result.message, "Unable to evaluate")
}

# ------Shape sanity Check------

test_result_details_structure if {
	result := control.result with input as collector_output([
		vba_setting("word", "3"),
		vba_setting("excel", "2"),
		vba_setting("ppt", "3"),
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