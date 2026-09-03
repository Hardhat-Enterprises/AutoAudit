package essential_eight.asd_essential_eight.v2025.test_e8_pa_1_1

import rego.v1

# NOTE: lastReportedDateTime below is an illustrative fixed date close to
# when this file was written, used for the "recent status" tests. Will
# need refreshing if the fixed date falls outside the 24 hour window by
# the time these tests are actually run.

test_compliant_all_conditions_met if {
	result := data.essential_eight.asd_essential_eight.v2025.control_e8_pa_1_1.result with input as {
		"protection_states": [
			{"device_id": "d1", "device_name": "Device1", "signatureUpdateOverdue": false, "realTimeProtectionEnabled": true, "lastReportedDateTime": "2026-09-03T00:00:00Z"},
			{"device_id": "d2", "device_name": "Device2", "signatureUpdateOverdue": false, "realTimeProtectionEnabled": true, "lastReportedDateTime": "2026-09-03T00:00:00Z"},
		],
		"software_inventory": [
			{"device_id": "d1", "softwareName": "Google Chrome", "numberOfWeaknesses": 0, "endOfSupportStatus": "Supported"},
		],
	}
	result.compliant == true
	count(result.details.devices_signature_overdue) == 0
	count(result.details.devices_realtime_protection_disabled) == 0
	count(result.details.software_exceeding_weakness_threshold) == 0
}

test_non_compliant_signature_overdue if {
	result := data.essential_eight.asd_essential_eight.v2025.control_e8_pa_1_1.result with input as {
		"protection_states": [
			{"device_id": "d1", "device_name": "Device1", "signatureUpdateOverdue": true, "realTimeProtectionEnabled": true, "lastReportedDateTime": "2026-09-03T00:00:00Z"},
		],
		"software_inventory": [],
	}
	result.compliant == false
	count(result.details.devices_signature_overdue) == 1
	contains(result.message, "signature overdue")
}

test_non_compliant_realtime_protection_disabled if {
	result := data.essential_eight.asd_essential_eight.v2025.control_e8_pa_1_1.result with input as {
		"protection_states": [
			{"device_id": "d1", "device_name": "Device1", "signatureUpdateOverdue": false, "realTimeProtectionEnabled": false, "lastReportedDateTime": "2026-09-03T00:00:00Z"},
		],
		"software_inventory": [],
	}
	result.compliant == false
	count(result.details.devices_realtime_protection_disabled) == 1
	contains(result.message, "real time protection disabled")
}

test_non_compliant_stale_status if {
	result := data.essential_eight.asd_essential_eight.v2025.control_e8_pa_1_1.result with input as {
		"protection_states": [
			{"device_id": "d1", "device_name": "Device1", "signatureUpdateOverdue": false, "realTimeProtectionEnabled": true, "lastReportedDateTime": "2023-01-01T00:00:00Z"},
		],
		"software_inventory": [],
	}
	result.compliant == false
	count(result.details.devices_stale_status) == 1
	contains(result.message, "have not reported status")
}

test_non_compliant_no_status if {
	result := data.essential_eight.asd_essential_eight.v2025.control_e8_pa_1_1.result with input as {
		"protection_states": [
			{"device_id": "d1", "device_name": "Device1", "signatureUpdateOverdue": false, "realTimeProtectionEnabled": true, "lastReportedDateTime": null},
		],
		"software_inventory": [],
	}
	result.compliant == false
	count(result.details.devices_no_status) == 1
}

test_non_compliant_weakness_exceeds_threshold if {
	result := data.essential_eight.asd_essential_eight.v2025.control_e8_pa_1_1.result with input as {
		"protection_states": [
			{"device_id": "d1", "device_name": "Device1", "signatureUpdateOverdue": false, "realTimeProtectionEnabled": true, "lastReportedDateTime": "2026-09-03T00:00:00Z"},
		],
		"software_inventory": [
			{"device_id": "d1", "softwareName": "Google Chrome", "numberOfWeaknesses": 1, "endOfSupportStatus": "Supported"},
		],
	}
	result.compliant == false
	count(result.details.software_exceeding_weakness_threshold) == 1
	contains(result.message, "exceed the weakness threshold")
}

test_compliant_at_zero_weaknesses if {
	result := data.essential_eight.asd_essential_eight.v2025.control_e8_pa_1_1.result with input as {
		"protection_states": [
			{"device_id": "d1", "device_name": "Device1", "signatureUpdateOverdue": false, "realTimeProtectionEnabled": true, "lastReportedDateTime": "2026-09-03T00:00:00Z"},
		],
		"software_inventory": [
			{"device_id": "d1", "softwareName": "Google Chrome", "numberOfWeaknesses": 0, "endOfSupportStatus": "Supported"},
		],
	}
	result.compliant == true
}

test_non_compliant_unsupported_software if {
	result := data.essential_eight.asd_essential_eight.v2025.control_e8_pa_1_1.result with input as {
		"protection_states": [
			{"device_id": "d1", "device_name": "Device1", "signatureUpdateOverdue": false, "realTimeProtectionEnabled": true, "lastReportedDateTime": "2026-09-03T00:00:00Z"},
		],
		"software_inventory": [
			{"device_id": "d1", "softwareName": "Old PDF Reader", "numberOfWeaknesses": 0, "endOfSupportStatus": "Unsupported"},
		],
	}
	result.compliant == false
	count(result.details.software_unsupported) == 1
	contains(result.message, "past vendor end of support")
}

test_non_compliant_multiple_devices_mixed_failures if {
	result := data.essential_eight.asd_essential_eight.v2025.control_e8_pa_1_1.result with input as {
		"protection_states": [
			{"device_id": "d1", "device_name": "Device1", "signatureUpdateOverdue": true, "realTimeProtectionEnabled": true, "lastReportedDateTime": "2026-09-03T00:00:00Z"},
			{"device_id": "d2", "device_name": "Device2", "signatureUpdateOverdue": false, "realTimeProtectionEnabled": true, "lastReportedDateTime": "2026-09-03T00:00:00Z"},
		],
		"software_inventory": [],
	}
	result.compliant == false
	count(result.details.devices_signature_overdue) == 1
}

test_non_compliant_nothing_configured if {
	result := data.essential_eight.asd_essential_eight.v2025.control_e8_pa_1_1.result with input as {
		"protection_states": [],
		"software_inventory": [],
	}
	result.compliant == true
	result.details.total_devices == 0
	result.details.total_covered_software == 0
}

test_result_details_structure if {
	result := data.essential_eight.asd_essential_eight.v2025.control_e8_pa_1_1.result with input as {
		"protection_states": [
			{"device_id": "d1", "device_name": "Device1", "signatureUpdateOverdue": false, "realTimeProtectionEnabled": true, "lastReportedDateTime": "2026-09-03T00:00:00Z"},
		],
		"software_inventory": [],
	}
	_ = result.compliant
	_ = result.message
	_ = result.details.devices_signature_overdue
	_ = result.details.devices_realtime_protection_disabled
	_ = result.details.devices_stale_status
	_ = result.details.devices_no_status
	_ = result.details.software_exceeding_weakness_threshold
	_ = result.details.weakness_threshold
	_ = result.details.software_unsupported
	_ = result.details.total_devices
	_ = result.details.total_covered_software
}
