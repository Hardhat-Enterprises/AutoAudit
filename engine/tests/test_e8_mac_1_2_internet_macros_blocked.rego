package essential_eight.asd_essential_eight.v2025.test_e8_mac_1_2

import rego.v1

control := data.essential_eight.asd_essential_eight.v2025.control_e8_mac_1_2

app_prefix := {
	"word": "user_vendor_msft_policy_config_word16v2~policy~l_microsoftofficeword~l_wordoptions~l_security~l_trustcenter_l_blockmacroexecutionfrominternet",
	"excel": "user_vendor_msft_policy_config_excel16v2~policy~l_microsoftofficeexcel~l_exceloptions~l_security~l_trustcenter_l_blockmacroexecutionfrominternet",
	"ppt": "user_vendor_msft_policy_config_ppt16v2~policy~l_microsoftofficepowerpoint~l_powerpointoptions~l_security~l_trustcenter_l_blockmacroexecutionfrominternet",
}

internet_setting(app, enabled) := {"settingInstance": {
	"settingDefinitionId": app_prefix[app],
	"choiceSettingValue": {
		"value": sprintf("%s_%s", [app_prefix[app], enabled]),
		"children": [],
	},
}}

# A value with no _N suffix. An endswith check would misread it as enabled.
internet_setting_unsuffixed(app) := {"settingInstance": {
	"settingDefinitionId": app_prefix[app],
	"choiceSettingValue": {
		"value": app_prefix[app],
		"children": [],
	},
}}

vba_setting := {"settingInstance": {
	"settingDefinitionId": "user_vendor_msft_policy_config_word16v2~policy~l_microsoftofficeword~l_wordoptions~l_security~l_trustcenter_l_vbawarningspolicy",
	"choiceSettingValue": {
		"value": "user_vendor_msft_policy_config_word16v2~policy~l_microsoftofficeword~l_wordoptions~l_security~l_trustcenter_l_vbawarningspolicy_1",
		"children": [{"choiceSettingValue": {"value": "..._l_empty19_2", "children": []}}],
	},
}}

# The policy only counts assignments, so the target shape is not significant here.
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
		"id": "p1",
		"name": "E8_MACRO",
		"assignments": [group_assignment],
		"settings": settings,
	}],
	"total_configuration_policies": 1,
}

# Configured correctly, but no device receives it.
collector_output_unassigned(settings) := {
	"configuration_policies": [{
		"id": "p1",
		"name": "E8_MACRO",
		"assignments": [],
		"settings": settings,
	}],
	"total_configuration_policies": 1,
}

# Matches the live MSFT sandbox tenant: all three apps enabled.
test_compliant_all_apps_blocked if {
	result := control.result with input as collector_output([
		internet_setting("word", "1"),
		internet_setting("excel", "1"),
		internet_setting("ppt", "1"),
	])

	result.compliant == true
	count(result.details.apps_not_configured) == 0
	count(result.details.apps_misconfigured) == 0
	contains(result.message, "are blocked")
}

test_compliant_across_multiple_policies if {
	result := control.result with input as {
		"configuration_policies": [
			{"id": "p1", "name": "Macro baseline - Office", "assignments": [group_assignment], "settings": [internet_setting("word", "1"), internet_setting("excel", "1")]},
			{"id": "p2", "name": "Macro baseline - PowerPoint", "assignments": [group_assignment], "settings": [internet_setting("ppt", "1")]},
		],
		"total_configuration_policies": 2,
	}

	result.compliant == true
	result.details.internet_block_settings_found == 3
}

test_non_compliant_setting_disabled if {
	result := control.result with input as collector_output([
		internet_setting("word", "0"),
		internet_setting("excel", "0"),
		internet_setting("ppt", "0"),
	])

	result.compliant == false
	result.details.apps_misconfigured == ["Excel", "PowerPoint", "Word"]
	count(result.details.apps_not_configured) == 0
}

test_non_compliant_one_app_disabled if {
	result := control.result with input as collector_output([
		internet_setting("word", "1"),
		internet_setting("excel", "1"),
		internet_setting("ppt", "0"),
	])

	result.compliant == false
	result.details.compliant_apps == ["Excel", "Word"]
	result.details.apps_misconfigured == ["PowerPoint"]
}

test_non_compliant_only_excel_configured if {
	result := control.result with input as collector_output([internet_setting("excel", "1")])

	result.compliant == false
	result.details.compliant_apps == ["Excel"]
	result.details.apps_not_configured == ["PowerPoint", "Word"]
	contains(result.message, "Not configured: PowerPoint, Word")
}

test_non_compliant_unsuffixed_value_is_not_enabled if {
	result := control.result with input as collector_output([
		internet_setting_unsuffixed("word"),
		internet_setting_unsuffixed("excel"),
		internet_setting_unsuffixed("ppt"),
	])

	result.compliant == false
	result.details.apps_misconfigured == ["Excel", "PowerPoint", "Word"]
}

# A different macro setting must not be mistaken for this one.
test_non_compliant_vba_setting_alone_does_not_satisfy_this_control if {
	result := control.result with input as collector_output([vba_setting])

	result.compliant == false
	result.details.internet_block_settings_found == 0
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

# The debug wrapper saved to sample files is not the runtime input shape.
test_harness_wrapped_input_is_not_accepted if {
	result := control.result with input as {"data": collector_output([
		internet_setting("word", "1"),
		internet_setting("excel", "1"),
		internet_setting("ppt", "1"),
	])}

	result.compliant == false
	contains(result.message, "Unable to evaluate")
}

# --- Assignment coverage -----------------------------------------------------

test_non_compliant_enabled_but_policy_unassigned if {
	result := control.result with input as collector_output_unassigned([
		internet_setting("word", "1"),
		internet_setting("excel", "1"),
		internet_setting("ppt", "1"),
	])

	result.compliant == false
	result.details.apps_unassigned == ["Excel", "PowerPoint", "Word"]
	result.details.compliant_apps == []
}

test_non_compliant_assigned_but_setting_disabled if {
	result := control.result with input as collector_output([
		internet_setting("word", "0"),
		internet_setting("excel", "0"),
		internet_setting("ppt", "0"),
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
				"settings": [internet_setting("word", "1"), internet_setting("excel", "1")],
			},
			{
				"id": "p2", "name": "Draft, never assigned",
				"assignments": [],
				"settings": [internet_setting("ppt", "1")],
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
			"settings": [internet_setting("word", "1"), internet_setting("excel", "1"), internet_setting("ppt", "1")],
		}],
		"total_configuration_policies": 1,
	}

	result.compliant == false
}
