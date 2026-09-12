# METADATA
# title: Standardize Time Synchronization (GCP)
# description: |
#   Organisations must standardize time synchronization by configuring at least two synchronized time
#   sources across enterprise assets, where supported.
#   For Compute Engine fleets, consistent time synchronisation should be enforced via OS Config guest
#   policies or managed configuration for chrony, ntpd, or Windows Time Service as applicable. Compliance
#   must be validated through OS Config reports and spot-checked instance time sync status.
# related_resources:
# - ref: https://cloud.google.com/compute/docs/instances/managing-instance-access
#   description: OS Config Guest Policy Documentation
# - ref: https://cloud.google.com/compute/docs/instances/vm-instance-metadata
#   description: Compute Engine Time Synchronisation Documentation
# custom:
#   control_id: CIS-8.4
#   framework: cis
#   benchmark: gcp-foundations
#   version: v2.0.0
#   severity: low
#   service: OS Config / Compute Engine
#   requires_permissions:
#   - osconfig.patchDeployments.list
#   - osconfig.inventories.get
#   - compute.instances.list

package cis.gcp_foundations.v2_0_0.control_8_4

import rego.v1

# Default result
default result := {
	"compliant": false,
	"message": "Evaluation failed: insufficient data to verify time synchronization",
	"details": {},
}

default compliant := false

# ---------------------------
# Compliance Logic
# ---------------------------
compliant if {
	count(input.time_sources) >= 2
	input.policy_enforced == true
	input.policy_assignment_scope != ""
	fleet_compliance_confirmed
	has_sample_instance_evidence
}

# The OS Config compliance report must cover at least one instance/group, and every
# entry in it must be compliant -- partial or unreported coverage isn't fleet-wide enforcement
fleet_compliance_confirmed if {
	count(input.os_config_compliance) > 0
	every c in input.os_config_compliance {
		c.compliant == true
	}
}

# At least one instance must have a real, time-stamped status check confirming it is
# synced and using two or more of the configured time sources
has_sample_instance_evidence if {
	some instance in input.sample_instance_status
	instance.synced == true
	count(instance.sources) >= 2
	instance.timestamp != ""
}

# ---------------------------
# Result Output
# ---------------------------
result := output if {
	os_config_compliance := get_array(input, "os_config_compliance")
	sample_instance_status := get_array(input, "sample_instance_status")

	output := {
		"compliant": compliant,
		"message": generate_message,
		"affected_resources": os_config_compliance,
		"details": {
			"time_source_count": count(input.time_sources),
			"policy_enforced": input.policy_enforced,
			"policy_assignment_scope": input.policy_assignment_scope,
			"fleet_instance_count": count(os_config_compliance),
			"sample_instance_count": count(sample_instance_status),
			"requires_example_evidence": true,
		},
	}
}

# ---------------------------
# Message Logic
# ---------------------------
generate_message := msg if {
	count(input.time_sources) < 2
	msg := "FAIL: Fewer than two time sources are configured"
}

generate_message := msg if {
	count(input.time_sources) >= 2
	not input.policy_enforced
	msg := "FAIL: Time synchronization is not enforced via policy across enterprise assets"
}

generate_message := msg if {
	input.policy_enforced
	input.policy_assignment_scope == ""
	msg := "FAIL: Time synchronization policy has no defined assignment scope"
}

generate_message := msg if {
	input.policy_assignment_scope != ""
	not fleet_compliance_confirmed
	msg := "FAIL: OS Config compliance evidence does not confirm the policy is applied across the fleet"
}

generate_message := msg if {
	fleet_compliance_confirmed
	not has_sample_instance_evidence
	msg := "INCONCLUSIVE: No instance-level status output found confirming synced state and configured sources"
}

generate_message := msg if {
	compliant
	msg := "PASS: At least two time sources are configured and enforced across the fleet, with instance evidence confirming synchronization"
}

# ---------------------------
# Helper Functions
# ---------------------------
get_array(obj, key) := value if {
	value := obj[key]
} else := []
