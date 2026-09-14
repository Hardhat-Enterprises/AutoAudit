package essential_eight.asd_essential_eight.v2025.test_e8_ac_1_1

import rego.v1

test_compliant_enforced_and_assigned_tenant_wide if {
	result := data.essential_eight.asd_essential_eight.v2025.control_e8_ac_1_1.result with input as {
		"policies_found": 2,
		"weakest_policy_name": "Workstations-AppLocker-Enforce",
		"graph_source_type": "legacy_device_configuration",
		"graph_policy_id": "00000000-1111-2222-3333-444444444444",
		"configured_enforcement_state": "enforced",
		"trust_reputation": false,
		"trust_managed_installer": false,
		"assignment_scope": "all_devices",
		"has_exclusions": false,
		"effective_device_state_verified": false,
	}

	result.compliant == true
	result.details.assessment_state == "compliant"
	result.details.deployment_confirmed == true
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
		"assignment_scope": "all_devices",
		"has_exclusions": false,
		"effective_device_state_verified": false,
	}

	# Audit mode records execution but blocks nothing, so it cannot satisfy the
	# control however widely it is deployed.
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
		"assignment_scope": "none",
		"has_exclusions": false,
		"effective_device_state_verified": false,
	}

	# Absence of an Intune policy is not evidence of failure: application control
	# may be enforced by another mechanism.
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
		"assignment_scope": "all_devices",
		"has_exclusions": false,
		"effective_device_state_verified": false,
	}

	# A custom-XML policy the collector cannot interpret must not pass and must
	# not be reported as a confirmed failure.
	result.compliant == false
	result.details.assessment_state == "insufficient_evidence"
}

test_insufficient_evidence_group_scoped_assignment if {
	result := data.essential_eight.asd_essential_eight.v2025.control_e8_ac_1_1.result with input as {
		"policies_found": 1,
		"weakest_policy_name": "Pilot-Ring-AppControl",
		"graph_source_type": "modern_configuration_policy",
		"graph_policy_id": "22222222-3333-4444-5555-666666666666",
		"configured_enforcement_state": "enforced",
		"trust_reputation": false,
		"trust_managed_installer": true,
		"assignment_scope": "group_scoped",
		"has_exclusions": false,
		"effective_device_state_verified": false,
	}

	# A correctly enforced policy targeted at a single group may reach only a
	# pilot fleet. Coverage of the required workstations cannot be established
	# from configuration, so this must not certify the tenant as compliant.
	result.compliant == false
	result.details.assessment_state == "insufficient_evidence"
	result.details.deployment_confirmed == false
}

test_insufficient_evidence_assignment_with_exclusions if {
	result := data.essential_eight.asd_essential_eight.v2025.control_e8_ac_1_1.result with input as {
		"policies_found": 1,
		"weakest_policy_name": "AllDevices-AppControl-WithExclusions",
		"graph_source_type": "modern_configuration_policy",
		"graph_policy_id": "33333333-4444-5555-6666-777777777777",
		"configured_enforcement_state": "enforced",
		"trust_reputation": false,
		"trust_managed_installer": true,
		"assignment_scope": "all_devices",
		"has_exclusions": true,
		"effective_device_state_verified": false,
	}

	# A tenant-wide assignment carrying exclusion groups no longer demonstrates
	# full coverage, since the excluded devices cannot be enumerated here.
	result.compliant == false
	result.details.assessment_state == "insufficient_evidence"
	result.details.has_exclusions == true
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
		"assignment_scope": "all_devices",
		"has_exclusions": false,
		"effective_device_state_verified": false,
	}

	# Enforced and deployed, but trust based on Intelligent Security Graph
	# reputation alone is not an organisation approved set.
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
		"assignment_scope": "none",
		"has_exclusions": false,
		"effective_device_state_verified": false,
	}

	# A correctly configured policy that reaches no device enforces nothing. This
	# is a confirmed failure rather than missing evidence.
	result.compliant == false
	result.details.assessment_state == "non_compliant"
}
