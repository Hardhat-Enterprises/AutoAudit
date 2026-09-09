# METADATA
# title: Collect Detailed Audit Logs (GCP)
# description: |
#   Organisations must configure detailed audit logging for enterprise assets containing sensitive data,
#   including event source, date, username, timestamp, source addresses, destination addresses, and
#   other elements useful for forensic investigation.
#   For sensitive projects and datasets, detailed audit log categories -- including Data Access logs for
#   services such as BigQuery, Cloud Storage, Cloud SQL, and Cloud KMS -- should be enabled where
#   appropriate, with logs routed to the central destination and access protected by least privilege.
# related_resources:
# - ref: https://cloud.google.com/logging/docs/audit#data-access
#   description: Data Access Audit Logs Documentation
# - ref: https://cloud.google.com/logging/docs/audit
#   description: Cloud Audit Logs Documentation
# custom:
#   control_id: CIS-8.5
#   framework: cis
#   benchmark: gcp-foundations
#   version: v2.0.0
#   severity: medium
#   service: Cloud Logging
#   requires_permissions:
#   - logging.settings.get
#   - logging.logEntries.list
#   - resourcemanager.projects.getIamPolicy

package cis.gcp_foundations.v2_0_0.control_8_5

import rego.v1

# Default result
default result := {
	"compliant": false,
	"message": "Evaluation failed: insufficient data to verify detailed audit logging",
	"details": {},
}

default compliant := false

# ---------------------------
# Compliance Logic
# ---------------------------
compliant if {
	sensitive_scope_defined
	input.data_access_logging_enabled == true
	has_detailed_sample_log_entry
}

# The sensitive boundary must be explicitly listed - each entry needs a resource
# identifier and the label/tag/folder placement that marks it as sensitive.
# Without this, reviewers can't confirm what was actually treated as sensitive
sensitive_scope_defined if {
	count(input.sensitive_scope) > 0
	every s in input.sensitive_scope {
		s.resource_id != ""
		s.label_or_tag != ""
	}
}

# At least one exported log entry must show the richer forensic fields -
# identity, resource, method, and timestamp - not just basic event logging
has_detailed_sample_log_entry if {
	some entry in input.sample_log_entries
	entry.principal_email != ""
	entry.resource_name != ""
	entry.method_name != ""
	entry.timestamp != ""
}

# ---------------------------
# Result Output
# ---------------------------
result := output if {
	sensitive_scope := get_array(input, "sensitive_scope")
	sample_log_entries := get_array(input, "sample_log_entries")

	output := {
		"compliant": compliant,
		"message": generate_message,
		"affected_resources": sensitive_scope,
		"details": {
			"sensitive_scope_count": count(sensitive_scope),
			"data_access_logging_enabled": input.data_access_logging_enabled,
			"sample_log_entry_count": count(sample_log_entries),
			"requires_example_evidence": true,
		},
	}
}

# ---------------------------
# Message Logic
# ---------------------------
generate_message := msg if {
	not sensitive_scope_defined
	msg := "FAIL: Sensitive assets have not been identified or scoped"
}

generate_message := msg if {
	sensitive_scope_defined
	not input.data_access_logging_enabled
	msg := "FAIL: Detailed audit logging is not enabled for the identified sensitive assets"
}

generate_message := msg if {
	input.data_access_logging_enabled
	not has_detailed_sample_log_entry
	msg := "INCONCLUSIVE: No sample log entry found showing the detailed fields needed for forensic review"
}

generate_message := msg if {
	compliant
	msg := "PASS: Sensitive assets are identified, detailed audit logging is enabled, and sample logs confirm the richer fields required for investigation"
}

# ---------------------------
# Helper Functions
# ---------------------------
get_array(obj, key) := value if {
	value := obj[key]
} else := []
