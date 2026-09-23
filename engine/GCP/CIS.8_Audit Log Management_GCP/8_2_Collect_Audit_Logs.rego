# METADATA
# title: Collect Audit Logs (GCP)
# description: |
#   Organisations must collect audit logs and ensure that logging, per the enterprise's audit log
#   management process, has been enabled across enterprise assets.
#   Cloud Audit Logs should be enabled at the organisation or folder level so coverage is consistent
#   and new projects inherit the baseline. Logs must be routed to a central destination using Logs
#   Router sinks, and collection must be validated by sampling real log entries for key services and
#   administrative actions.
# related_resources:
# - ref: https://cloud.google.com/logging/docs/audit
#   description: Cloud Audit Logs Documentation
# - ref: https://cloud.google.com/logging/docs/export/configure_export_v2
#   description: Logs Router Sink Configuration Documentation
# custom:
#   control_id: CIS-8.2
#   framework: cis
#   benchmark: gcp-foundations
#   version: v2.0.0
#   severity: medium
#   service: Cloud Logging
#   requires_permissions:
#   - logging.sinks.list
#   - logging.settings.get
#   - logging.logEntries.list

package cis.gcp_foundations.v2_0_0.control_8_2

import rego.v1

# Default result
default result := {
	"compliant": false,
	"message": "Evaluation failed: insufficient data to verify audit log collection",
	"details": {},
}

default compliant := false

# ---------------------------
# Compliance Logic
# ---------------------------
compliant if {
	scope_defined
	input.audit_log_categories_enabled == true
	central_sink_configured
	has_sample_log_entry
}

# Config evidence must show which org or folder the logging applies to --
# without this, coverage can't be confirmed as consistent rather than ad hoc
scope_defined if {
	input.audit_log_scope_type in {"organization", "folder"}
	input.audit_log_scope_identifier != ""
}

# At least one sink must route logs to a central destination and cover child
# projects/folders, matching the 8.1 requirement for centralised routing
central_sink_configured if {
	some sink in input.sinks
	sink.include_children == true
	sink.destination != ""
}

# At least one real, time-stamped log entry must be present with the key
# fields needed to confirm events are actually being generated and captured
has_sample_log_entry if {
	some entry in input.sample_log_entries
	entry.principal_email != ""
	entry.service_name != ""
	entry.method_name != ""
	entry.timestamp != ""
}

# ---------------------------
# Result Output
# ---------------------------
result := output if {
	sinks := get_array(input, "sinks")
	sample_log_entries := get_array(input, "sample_log_entries")

	output := {
		"compliant": compliant,
		"message": generate_message,
		"affected_resources": sinks,
		"details": {
			"audit_log_scope_type": input.audit_log_scope_type,
			"audit_log_scope_identifier": input.audit_log_scope_identifier,
			"audit_log_categories_enabled": input.audit_log_categories_enabled,
			"sink_count": count(sinks),
			"sample_log_entry_count": count(sample_log_entries),
			"requires_example_evidence": true,
		},
	}
}

# ---------------------------
# Message Logic
# ---------------------------
generate_message := msg if {
	not scope_defined
	msg := "FAIL: Cannot confirm audit logging scope at organisation or folder level"
}

generate_message := msg if {
	scope_defined
	not input.audit_log_categories_enabled
	msg := "FAIL: Audit logging is not enabled broadly at the confirmed scope"
}

generate_message := msg if {
	input.audit_log_categories_enabled
	not central_sink_configured
	msg := "FAIL: No sink found that routes audit logs centrally with child resource coverage"
}

generate_message := msg if {
	central_sink_configured
	not has_sample_log_entry
	msg := "INCONCLUSIVE: No sample log entry provided to confirm events are being generated and captured"
}

generate_message := msg if {
	compliant
	msg := "PASS: Audit logging is enabled at the intended scope, routed centrally, and sample log entries confirm events are being captured"
}

# ---------------------------
# Helper Functions
# ---------------------------
get_array(obj, key) := value if {
	value := obj[key]
} else := []
