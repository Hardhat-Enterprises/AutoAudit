# METADATA
# title: Collect Command-Line Audit Logs (GCP)
# description: |
#   Organisations must collect command-line audit logs, such as from PowerShell, BASH, and remote
#   administrative terminals.
#   On managed VMs, host-level auditing for interactive and privileged command execution should be
#   enabled and shipped to Cloud Logging. OS Config should be used to deploy and maintain a consistent
#   auditing baseline (auditd on Linux, process creation and PowerShell logging on Windows), with logs
#   confirmed as searchable and tied to instance identity and user context.
# related_resources:
# - ref: https://cloud.google.com/compute/docs/instances/managing-instance-access
#   description: OS Config Guest Policy Documentation
# - ref: https://cloud.google.com/logging/docs/agent/logging/configuration
#   description: Cloud Logging Agent Configuration Documentation
# custom:
#   control_id: CIS-8.8
#   framework: cis
#   benchmark: gcp-foundations
#   version: v2.0.0
#   severity: medium
#   service: OS Config / Compute Engine / Cloud Logging
#   requires_permissions:
#   - osconfig.patchDeployments.list
#   - osconfig.inventories.get
#   - logging.logEntries.list

package cis.gcp_foundations.v2_0_0.control_8_8

import rego.v1

# Default result
default result := {
	"compliant": false,
	"message": "Evaluation failed: insufficient data to verify command-line audit logging",
	"details": {},
}

default compliant := false

# ---------------------------
# Compliance Logic
# ---------------------------
compliant if {
	input.audit_policy_configured == true
	input.audit_policy_scope != ""
	fleet_compliance_confirmed
	has_sample_command_log_entry
}

# The OS Config compliance report must cover at least one instance/group, and every
# entry in it must be compliant - same fleet-wide coverage check used in 8.4
fleet_compliance_confirmed if {
	count(input.os_config_compliance) > 0
	every c in input.os_config_compliance {
		c.compliant == true
	}
}

# At least one real command execution event must be present, tied to a specific
# instance and user, proving auditing is producing usable data, not just configured
has_sample_command_log_entry if {
	some entry in input.sample_command_log_entries
	entry.instance_id != ""
	entry.user != ""
	entry.command != ""
	entry.timestamp != ""
}

# ---------------------------
# Result Output
# ---------------------------
result := output if {
	os_config_compliance := get_array(input, "os_config_compliance")
	sample_command_log_entries := get_array(input, "sample_command_log_entries")

	output := {
		"compliant": compliant,
		"message": generate_message,
		"affected_resources": os_config_compliance,
		"details": {
			"audit_policy_configured": input.audit_policy_configured,
			"audit_policy_scope": input.audit_policy_scope,
			"fleet_instance_count": count(os_config_compliance),
			"sample_command_log_entry_count": count(sample_command_log_entries),
			"requires_example_evidence": true,
		},
	}
}

# ---------------------------
# Message Logic
# ---------------------------
generate_message := msg if {
	not input.audit_policy_configured
	msg := "FAIL: No host-level command auditing baseline is configured"
}

generate_message := msg if {
	input.audit_policy_configured
	input.audit_policy_scope == ""
	msg := "FAIL: Command auditing policy has no defined assignment scope"
}

generate_message := msg if {
	input.audit_policy_scope != ""
	not fleet_compliance_confirmed
	msg := "FAIL: OS Config compliance evidence does not confirm the auditing policy is applied across the fleet"
}

generate_message := msg if {
	fleet_compliance_confirmed
	not has_sample_command_log_entry
	msg := "INCONCLUSIVE: No command execution log entry found tied to a specific instance and user"
}

generate_message := msg if {
	compliant
	msg := "PASS: Command-line auditing is configured and applied across the fleet, with log evidence confirming command execution events are captured"
}

# ---------------------------
# Helper Functions
# ---------------------------
get_array(obj, key) := value if {
	value := obj[key]
} else := []
