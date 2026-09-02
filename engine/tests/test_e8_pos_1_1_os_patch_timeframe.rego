package essential_eight.asd_essential_eight.v2025.test_e8_pos_1_1

import rego.v1

test_compliant_slowest_ring_at_threshold if {
	result := data.essential_eight.asd_essential_eight.v2025.control_e8_pos_1_1.result with input as {
		"profiles_found": 3,
		"weakest_profile_name": "Ring 3 - Critical Devices",
		"quality_updates_deferral_days": 10,
		"quality_updates_deadline_days": 2,
		"deadline_grace_period_days": 2,
		"days_to_active": 14,
		"quality_updates_paused": false,
		"automatic_update_mode": "auto_install_and_reboot",
	}
	result.compliant == true
	result.details.days_to_active == 14
	result.details.threshold_exceeded == false
}

test_non_compliant_timeframe_exceeded if {
	result := data.essential_eight.asd_essential_eight.v2025.control_e8_pos_1_1.result with input as {
		"profiles_found": 3,
		"weakest_profile_name": "Ring 3 - Critical Devices",
		"quality_updates_deferral_days": 11,
		"quality_updates_deadline_days": 2,
		"deadline_grace_period_days": 2,
		"days_to_active": 15,
		"quality_updates_paused": false,
		"automatic_update_mode": "auto_install_and_reboot",
	}
	result.compliant == false
	result.details.threshold_exceeded == true
}

test_non_compliant_no_profile_found if {
	result := data.essential_eight.asd_essential_eight.v2025.control_e8_pos_1_1.result with input as {
		"profiles_found": 0,
		"weakest_profile_name": null,
		"quality_updates_deferral_days": 0,
		"quality_updates_deadline_days": 0,
		"deadline_grace_period_days": 0,
		"days_to_active": 0,
		"quality_updates_paused": false,
		"automatic_update_mode": "not_configured",
	}
	result.compliant == false
	result.details.profiles_found == 0

	# The Autopatch case must remain distinguishable from an ordinary failure:
	# absence of a profile is "verify manually", not "the tenant is non-compliant".
	result.message == "No Windows Update for Business profile detected - tenant may be managed by Windows Autopatch, manual verification required"
}

test_non_compliant_updates_paused if {
	result := data.essential_eight.asd_essential_eight.v2025.control_e8_pos_1_1.result with input as {
		"profiles_found": 1,
		"weakest_profile_name": "Ring 1 - Pilot",
		"quality_updates_deferral_days": 0,
		"quality_updates_deadline_days": 2,
		"deadline_grace_period_days": 2,
		"days_to_active": 4,
		"quality_updates_paused": true,
		"automatic_update_mode": "auto_install",
	}
	result.compliant == false
	result.details.quality_updates_paused == true
}

test_non_compliant_user_controlled_install if {
	result := data.essential_eight.asd_essential_eight.v2025.control_e8_pos_1_1.result with input as {
		"profiles_found": 1,
		"weakest_profile_name": "Ring 1 - Pilot",
		"quality_updates_deferral_days": 0,
		"quality_updates_deadline_days": 2,
		"deadline_grace_period_days": 2,
		"days_to_active": 4,
		"quality_updates_paused": false,
		"automatic_update_mode": "notify_download",
	}
	result.compliant == false
}

test_non_compliant_unknown_mode_fails_closed if {
	result := data.essential_eight.asd_essential_eight.v2025.control_e8_pos_1_1.result with input as {
		"profiles_found": 1,
		"weakest_profile_name": "Ring 1 - Pilot",
		"quality_updates_deferral_days": 0,
		"quality_updates_deadline_days": 2,
		"deadline_grace_period_days": 2,
		"days_to_active": 4,
		"quality_updates_paused": false,
		"automatic_update_mode": "unknown",
	}
	result.compliant == false
}
