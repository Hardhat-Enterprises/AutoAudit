package cis.microsoft_365_foundations.v6_0_0.test_control_5_1_4_6

import rego.v1

test_recovery_restricted_is_compliant if {
	result := data.cis.microsoft_365_foundations.v6_0_0.control_5_1_4_6.result with input as {"allowed_to_read_bitlocker_keys_for_owned_device": false}

	result.compliant == true
	result.message == "Users are restricted from recovering BitLocker keys (allowedToReadBitlockerKeysForOwnedDevice=false)"
	result.details.allowed_to_read_bitlocker_keys_for_owned_device == false
}

test_recovery_allowed_is_non_compliant if {
	result := data.cis.microsoft_365_foundations.v6_0_0.control_5_1_4_6.result with input as {"allowed_to_read_bitlocker_keys_for_owned_device": true}

	result.compliant == false
	result.message == "Users can recover BitLocker keys (allowedToReadBitlockerKeysForOwnedDevice=true)"
	result.details.allowed_to_read_bitlocker_keys_for_owned_device == true
}

test_null_reports_unknown if {
	result := data.cis.microsoft_365_foundations.v6_0_0.control_5_1_4_6.result with input as {"allowed_to_read_bitlocker_keys_for_owned_device": null}

	result.compliant == false
	result.message == "Unable to determine allowedToReadBitlockerKeysForOwnedDevice"
	result.details.allowed_to_read_bitlocker_keys_for_owned_device == null
}

test_missing_setting_reports_unknown if {
	result := data.cis.microsoft_365_foundations.v6_0_0.control_5_1_4_6.result with input as {"unrelated_setting": false}

	result.compliant == false
	result.message == "Unable to determine allowedToReadBitlockerKeysForOwnedDevice"
	result.details == {}
}

test_empty_input_reports_unknown if {
	result := data.cis.microsoft_365_foundations.v6_0_0.control_5_1_4_6.result with input as {}

	result.compliant == false
	result.message == "Unable to determine allowedToReadBitlockerKeysForOwnedDevice"
	result.details == {}
}

test_invalid_types_report_unknown if {
	invalid_values := ["false", "true", "", 0, 1, [], {}, [false]]

	every value in invalid_values {
		result := data.cis.microsoft_365_foundations.v6_0_0.control_5_1_4_6.result with input as {"allowed_to_read_bitlocker_keys_for_owned_device": value}

		result.compliant == false
		result.message == "Unable to determine allowedToReadBitlockerKeysForOwnedDevice"
		result.details.allowed_to_read_bitlocker_keys_for_owned_device == value
	}
}
