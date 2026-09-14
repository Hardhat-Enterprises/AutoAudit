# METADATA
# title: Establish and Maintain an Audit Log Management Process (GCP)
# description: |
#   Organisations must establish and maintain a documented audit log management process that defines
#   logging requirements, including the collection, review, and retention of audit logs for enterprise
#   assets. The documented process must be reviewed and updated annually, or when significant enterprise
#   changes occur.
#   Org or folder-level audit log configuration and Logs Router sink inventory must be validated against
#   the documented standard, with a time-stamped artefact showing the process is actively being used.
# related_resources:
# - ref: https://cloud.google.com/logging/docs/audit
#   description: Cloud Audit Logs Documentation
# - ref: https://cloud.google.com/logging/docs/export/configure_export_v2
#   description: Logs Router Sink Configuration Documentation
# custom:
#   control_id: CIS-8.1
#   framework: cis
#   benchmark: gcp-foundations
#   version: v2.0.0
#   severity: medium
#   service: Cloud Logging / Cloud Asset Inventory
#   requires_permissions:
#   - logging.sinks.list
#   - logging.settings.get
#   - resourcemanager.organizations.get
#   - resourcemanager.folders.get

package cis.gcp_foundations.v2_0_0.control_8_1

import rego.v1

# Default result
default result := {
	"compliant": false,
	"message": "Evaluation failed: insufficient data to verify audit log management process",
	"details": {},
}

default compliant := false

# ---------------------------
# Compliance Logic
# ---------------------------
compliant if {
	input.logging_standard_documented == true
	input.logging_standard_owner != ""
	input.logging_standard_reviewed_within_12_months == true
	evidence_scope_visible
	audit_logging_enabled_at_scope
	central_sink_configured
	has_process_artefact_evidence
}

# Screenshots/evidence must clearly show which org or folder the config applies to --
# cropped or scope-less evidence cannot be used to confirm alignment with the standard
evidence_scope_visible if {
	input.audit_log_scope_type != ""
	input.audit_log_scope_identifier != ""
}

# Audit logging must be enabled at organisation or folder level (not ad hoc per project)
# so new projects inherit the baseline consistently
audit_logging_enabled_at_scope if {
	input.audit_log_scope_type in {"organization", "folder"}
	input.audit_log_categories_enabled == true
}

# At least one sink must route logs to a central destination and cover child
# projects/folders - a sink with no include-children coverage does not demonstrate centralisation
central_sink_configured if {
	some sink in input.sinks
	sink.include_children == true
	sink.destination != ""
}

# The documented process must be shown in active use via a dated artefact --
# e.g. a log review ticket, alert incident, or change record tied to the standard
has_process_artefact_evidence if {
	input.process_artefact_date != ""
	input.process_artefact_type != ""
}

# ---------------------------
# Result Output
# ---------------------------
result := output if {
	sinks := get_array(input, "sinks")

	output := {
		"compliant": compliant,
		"message": generate_message,
		"affected_resources": sinks,
		"details": {
			"logging_standard_documented": input.logging_standard_documented,
			"logging_standard_owner": input.logging_standard_owner,
			"logging_standard_reviewed_within_12_months": input.logging_standard_reviewed_within_12_months,
			"audit_log_scope_type": input.audit_log_scope_type,
			"audit_log_scope_identifier": input.audit_log_scope_identifier,
			"audit_log_categories_enabled": input.audit_log_categories_enabled,
			"sink_count": count(sinks),
			"process_artefact_date": input.process_artefact_date,
			"requires_example_evidence": true,
		},
	}
}

# ---------------------------
# Message Logic
# ---------------------------
generate_message := msg if {
	not input.logging_standard_documented
	msg := "FAIL: No documented audit log management process found"
}

generate_message := msg if {
	input.logging_standard_documented
	input.logging_standard_owner == ""
	msg := "INCONCLUSIVE: Documented process has no identifiable owner"
}

generate_message := msg if {
	input.logging_standard_owner != ""
	not input.logging_standard_reviewed_within_12_months
	msg := "FAIL: Documented audit log management process has not been reviewed within the last 12 months"
}

generate_message := msg if {
	input.logging_standard_reviewed_within_12_months
	not evidence_scope_visible
	msg := "INCONCLUSIVE: Configuration evidence does not clearly show the org or folder scope it applies to"
}

generate_message := msg if {
	evidence_scope_visible
	not audit_logging_enabled_at_scope
	msg := "FAIL: Audit logging is not enabled consistently at organisation or folder scope"
}

generate_message := msg if {
	audit_logging_enabled_at_scope
	not central_sink_configured
	msg := "FAIL: No sink found that routes audit logs centrally with child resource coverage"
}

generate_message := msg if {
	central_sink_configured
	not has_process_artefact_evidence
	msg := "INCONCLUSIVE: No time-stamped artefact found showing the logging process is actively used"
}

generate_message := msg if {
	compliant
	msg := "PASS: A documented, owned, and recently reviewed audit log management process is in place, and GCP configuration confirms consistent, centrally routed audit logging"
}

# ---------------------------
# Helper Functions
# ---------------------------
get_array(obj, key) := value if {
	value := obj[key]
} else := []
