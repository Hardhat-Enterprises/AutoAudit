package cis.microsoft_365_foundations.v6_0_0.test_control_7_2_9

import rego.v1

# --- Compliant ---

test_compliant_expiration_required_at_30_days if {
	result := data.cis.microsoft_365_foundations.v6_0_0.control_7_2_9.result with input as {
		"external_user_expiration_required": true,
		"external_user_expire_in_days": 30,
	}
	result.compliant == true
	contains(result.message, "expire automatically after 30 days")
}

# --- Non-compliant: expiration not required at all (tenant default) ---

test_non_compliant_expiration_not_required if {
	result := data.cis.microsoft_365_foundations.v6_0_0.control_7_2_9.result with input as {
		"external_user_expiration_required": false,
		"external_user_expire_in_days": 60,
	}
	result.compliant == false
	contains(result.message, "not set to expire")
	result.details.external_user_expire_in_days == 60
}

# --- Non-compliant: expiration required, but not at the recommended 30 days ---

test_non_compliant_wrong_day_count if {
	result := data.cis.microsoft_365_foundations.v6_0_0.control_7_2_9.result with input as {
		"external_user_expiration_required": true,
		"external_user_expire_in_days": 60,
	}
	result.compliant == false
}

test_non_compliant_fewer_than_30_days_still_fails_exact_match if {
	result := data.cis.microsoft_365_foundations.v6_0_0.control_7_2_9.result with input as {
		"external_user_expiration_required": true,
		"external_user_expire_in_days": 14,
	}
	result.compliant == false
}

# --- Non-compliant: expiration required but day count missing ---

test_non_compliant_days_missing if {
	result := data.cis.microsoft_365_foundations.v6_0_0.control_7_2_9.result with input as {
		"external_user_expiration_required": true,
	}
	result.compliant == false
	result.details.external_user_expire_in_days == null
}

# --- Fail closed: no evidence at all ---

test_unable_to_determine_when_missing if {
	result := data.cis.microsoft_365_foundations.v6_0_0.control_7_2_9.result with input as {}
	result.compliant == false
	result.message == "Unable to determine guest access expiration configuration"
}

test_unable_to_determine_when_flag_null if {
	result := data.cis.microsoft_365_foundations.v6_0_0.control_7_2_9.result with input as {
		"external_user_expiration_required": null,
		"external_user_expire_in_days": 30,
	}
	result.compliant == false
	result.message == "Unable to determine guest access expiration configuration"
}