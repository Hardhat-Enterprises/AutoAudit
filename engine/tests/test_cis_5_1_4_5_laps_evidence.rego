package cis.microsoft_365_foundations.v6_0_0.test_control_5_1_4_5

import rego.v1

test_enabled_laps_is_compliant if {
	result := data.cis.microsoft_365_foundations.v6_0_0.control_5_1_4_5.result with input as {
		"laps_enabled": true,
		"local_admin_password_settings": {"isEnabled": true},
	}

	result.compliant == true
	result.message == "Microsoft Entra Local Administrator Password Solution (LAPS) is enabled"
	result.details.laps_enabled == true
}

test_disabled_laps_is_non_compliant if {
	result := data.cis.microsoft_365_foundations.v6_0_0.control_5_1_4_5.result with input as {
		"laps_enabled": false,
		"local_admin_password_settings": {"isEnabled": false},
	}

	result.compliant == false
	result.message == "Microsoft Entra Local Administrator Password Solution (LAPS) is not enabled"
	result.details.laps_enabled == false
}

test_null_laps_reports_unknown if {
	result := data.cis.microsoft_365_foundations.v6_0_0.control_5_1_4_5.result with input as {
		"laps_enabled": null,
		"local_admin_password_settings": {},
	}

	result.compliant == false
	result.message == "Unable to determine whether LAPS is enabled"
}

test_missing_laps_reports_unknown if {
	result := data.cis.microsoft_365_foundations.v6_0_0.control_5_1_4_5.result with input as {"local_admin_password_settings": {}}

	result.compliant == false
	result.message == "Unable to determine whether LAPS is enabled"
}

test_invalid_laps_string_reports_unknown if {
	result := data.cis.microsoft_365_foundations.v6_0_0.control_5_1_4_5.result with input as {
		"laps_enabled": "true",
		"local_admin_password_settings": {"isEnabled": "true"},
	}

	result.compliant == false
	result.message == "Unable to determine whether LAPS is enabled"
}

test_invalid_laps_number_reports_unknown if {
	result := data.cis.microsoft_365_foundations.v6_0_0.control_5_1_4_5.result with input as {
		"laps_enabled": 1,
		"local_admin_password_settings": {"isEnabled": 1},
	}

	result.compliant == false
	result.message == "Unable to determine whether LAPS is enabled"
}

test_empty_input_reports_unknown if {
	result := data.cis.microsoft_365_foundations.v6_0_0.control_5_1_4_5.result with input as {}

	result.compliant == false
	result.message == "Unable to determine whether LAPS is enabled"
}
