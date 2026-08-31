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

collector_output(settings) := {
	"configuration_policies": [{
		"id": "3e6c6222-4466-401a-8b8d-5c7058c8d432",
		"name": "E8_MACRO",
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
			{"id": "p1", "name": "Macro baseline - Office", "settings": [vba_setting("word", "2"), vba_setting("excel", "2")]},
			{"id": "p2", "name": "Macro baseline - PowerPoint", "settings": [vba_setting("ppt", "4")]},
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

# Guards against the PR #311 mistake: the harness wrapper is not the runtime shape.
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
