package essential_eight.asd_essential_eight.v2025.test_e8_ac_1_1

import rego.v1

test_compliant_enforced_with_managed_installer if {
	result := data.essential_eight.asd_essential_eight.v2025.control_e8_ac_1_1.result with input as {
		"policies_found": 2,
		"weakest_policy_name": "Workstations-AppControl-Base",
		"policy_format": "built_in",
		"enforcement_mode": "enforced",
		"trust_reputation": false,
		"trust_managed_installer": true,
		"assigned": true,
	}

	result.compliant == true
	result.details.enforcement_mode == "enforced"
	result.details.reputation_only_trust == false
}

test_non_compliant_audit_only if {
	result := data.essential_eight.asd_essential_eight.v2025.control_e8_ac_1_1.result with input as {
		"policies_found": 1,
		"weakest_policy_name": "Pilot-AppControl-Audit",
		"policy_format": "built_in",
		"enforcement_mode": "audit_only",
		"trust_reputation": false,
		"trust_managed_installer": true,
		"assigned": true,
	}

	# Audit mode logs execution but blocks nothing, so it cannot satisfy the
	# control no matter how the trust options are configured.
	result.compliant == false
	result.details.enforcement_mode == "audit_only"
}

test_no_policy_found if {
	result := data.essential_eight.asd_essential_eight.v2025.control_e8_ac_1_1.result with input as {
		"policies_found": 0,
		"weakest_policy_name": null,
		"policy_format": "none",
		"enforcement_mode": "not_configured",
		"trust_reputation": false,
		"trust_managed_installer": false,
		"assigned": false,
	}

	result.compliant == false
	result.details.policies_found == 0

	# Absence of an Intune policy must remain distinguishable from an ordinary
	# failure: application control may be enforced by another mechanism.
	result.message == "No App Control for Business policy detected - application control may be enforced outside Intune, manual verification required"
}

test_non_compliant_reputation_only_trust if {
	result := data.essential_eight.asd_essential_eight.v2025.control_e8_ac_1_1.result with input as {
		"policies_found": 1,
		"weakest_policy_name": "Workstations-AppControl-ISG",
		"policy_format": "built_in",
		"enforcement_mode": "enforced",
		"trust_reputation": true,
		"trust_managed_installer": false,
		"assigned": true,
	}

	# Enforced, but trusting on Intelligent Security Graph reputation alone is
	# not an organisation approved set.
	result.compliant == false
	result.details.reputation_only_trust == true
}

test_non_compliant_policy_not_assigned if {
	result := data.essential_eight.asd_essential_eight.v2025.control_e8_ac_1_1.result with input as {
		"policies_found": 1,
		"weakest_policy_name": "Workstations-AppControl-Base",
		"policy_format": "built_in",
		"enforcement_mode": "enforced",
		"trust_reputation": false,
		"trust_managed_installer": true,
		"assigned": false,
	}

	# A correctly configured policy that reaches no device enforces nothing.
	result.compliant == false
	result.details.assigned == false
}

test_unknown_enforcement_mode_fails_closed if {
	result := data.essential_eight.asd_essential_eight.v2025.control_e8_ac_1_1.result with input as {
		"policies_found": 1,
		"weakest_policy_name": "Workstations-AppControl-Custom",
		"policy_format": "xml",
		"enforcement_mode": "unknown",
		"trust_reputation": false,
		"trust_managed_installer": true,
		"assigned": true,
	}

	# An enforcement value the collector does not recognise, including a custom
	# XML policy this collector cannot interpret, must fail rather than pass.
	result.compliant == false
}
