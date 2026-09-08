package essential_eight.asd_essential_eight.v2025.test_e8_ac_1_1

import rego.v1

test_compliant_enforced_legacy_profile if {
	result := data.essential_eight.asd_essential_eight.v2025.control_e8_ac_1_1.result with input as {
		"policies_found": 2,
		"weakest_policy_name": "Workstations-AppLocker-Enforce",
		"graph_source_type": "legacy_device_configuration",
		"graph_policy_id": "00000000-1111-2222-3333-444444444444",
		"configured_enforcement_state": "enforced",
		"trust_reputation": false,
		"trust_managed_installer": false,
		"assigned": true,
		"effective_device_state_verified": false,
	}

	result.compliant == true
	result.details.assessment_state == "compliant"
	result.details.configured_enforcement_state == "enforced"
}

test_non_compliant_audit_only if {
	result := data.essential_eight.asd_essential_eight.v2025.control_e8_ac_1_1.result with input as {
		"policies_found": 1,
		"weakest_policy_name": "Pilot-AppControl-Audit",
		"graph_source_type": "modern_configuration_policy",
		"graph_policy_id": "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee",
		"configured_enforcement_state": "audit_only",
		"trust_reputation": false,
		"trust_managed_installer": true,
		"assigned": true,
		"effective_device_state_verified": false,
	}

	# Audit mode records execution but blocks nothing, so it cannot satisfy the
	# control however the trust options are configured.
	result.compliant == false
	result.details.assessment_state == "non_compliant"
}

test_insufficient_evidence_no_policy_found if {
	result := data.essential_eight.asd_essential_eight.v2025.control_e8_ac_1_1.result with input as {
		"policies_found": 0,
		"weakest_policy_name": null,
		"graph_source_type": null,
		"graph_policy_id": null,
		"configured_enforcement_state": "not_configured",
		"trust_reputation": false,
		"trust_managed_installer": false,
		"assigned": false,
		"effective_device_state_verified": false,
	}

	# Absence of an Intune policy is not evidence of failure: application control
	# may be enforced by another mechanism. It must stay distinguishable from a
	# confirmed non-compliant result.
	result.compliant == false
	result.details.assessment_state == "insufficient_evidence"
	result.message == "No Intune application control policy detected - application control may be enforced by another mechanism, manual verification required"
}

test_insufficient_evidence_unknown_state if {
	result := data.essential_eight.asd_essential_eight.v2025.control_e8_ac_1_1.result with input as {
		"policies_found": 1,
		"weakest_policy_name": "Workstations-AppControl-CustomXML",
		"graph_source_type": "modern_configuration_policy",
		"graph_policy_id": "11111111-2222-3333-4444-555555555555",
		"configured_enforcement_state": "unknown",
		"trust_reputation": false,
		"trust_managed_installer": true,
		"assigned": true,
		"effective_device_state_verified": false,
	}

	# A custom-XML policy the collector cannot interpret, or an unrecognised
	# enum value, must not pass and must not be reported as a confirmed failure.
	result.compliant == false
	result.details.assessment_state == "insufficient_evidence"
}

test_non_compliant_reputation_only_trust if {
	result := data.essential_eight.asd_essential_eight.v2025.control_e8_ac_1_1.result with input as {
		"policies_found": 1,
		"weakest_policy_name": "Workstations-AppControl-ISG",
		"graph_source_type": "modern_configuration_policy",
		"graph_policy_id": "66666666-7777-8888-9999-000000000000",
		"configured_enforcement_state": "enforced",
		"trust_reputation": true,
		"trust_managed_installer": false,
		"assigned": true,
		"effective_device_state_verified": false,
	}

	# Enforced, but trust based on Intelligent Security Graph reputation alone is
	# not an organisation approved set.
	result.compliant == false
	result.details.reputation_only_trust == true
	result.details.assessment_state == "non_compliant"
}

test_non_compliant_policy_not_assigned if {
	result := data.essential_eight.asd_essential_eight.v2025.control_e8_ac_1_1.result with input as {
		"policies_found": 1,
		"weakest_policy_name": "Workstations-AppLocker-Enforce",
		"graph_source_type": "legacy_device_configuration",
		"graph_policy_id": "99999999-8888-7777-6666-555555555555",
		"configured_enforcement_state": "enforced",
		"trust_reputation": false,
		"trust_managed_installer": false,
		"assigned": false,
		"effective_device_state_verified": false,
	}

	# A correctly configured policy that reaches no device enforces nothing.
	result.compliant == false
	result.details.assigned == false
	result.details.assessment_state == "non_compliant"
}
