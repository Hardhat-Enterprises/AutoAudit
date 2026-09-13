# METADATA
# title: Centralize Audit Logs (GCP)
# description: |
#   Organisations must centralize, to the extent possible, audit log collection and retention across
#   enterprise assets in accordance with the documented audit log management process.
#   Organisation or folder-level Logs Router sinks with include-children should be used so audit logs
#   from projects flow into a central logging project, bucket, or downstream SIEM. Duties must be
#   separated by limiting who can read, export, or modify sinks and destinations, and centralisation
#   should be validated by querying for multiple log sources in the central destination.
# related_resources:
# - ref: https://cloud.google.com/logging/docs/export/aggregated_sinks
#   description: Aggregated Sink Documentation
# - ref: https://cloud.google.com/logging/docs/access-control
#   description: Cloud Logging Access Control Documentation
# custom:
#   control_id: CIS-8.9
#   framework: cis
#   benchmark: gcp-foundations
#   version: v2.0.0
#   severity: medium
#   service: Cloud Logging / IAM
#   requires_permissions:
#   - logging.sinks.list
#   - resourcemanager.organizations.getIamPolicy
#   - resourcemanager.folders.getIamPolicy

package cis.gcp_foundations.v2_0_0.control_8_9

import rego.v1

# Default result
default result := {
	"compliant": false,
	"message": "Evaluation failed: insufficient data to verify audit log centralisation",
	"details": {},
}

default compliant := false

# ---------------------------
# Compliance Logic
# ---------------------------
compliant if {
	sinks_defined_at_scope
	input.destination_access_restricted == true
	has_multi_source_evidence
}

# Every sink in use must be defined at org or folder scope, include child resources,
# and have a real destination - a sink missing any of these can't demonstrate
# true centralisation rather than per-project logging
sinks_defined_at_scope if {
	count(input.sinks) > 0
	every s in input.sinks {
		s.scope_type in {"organization", "folder"}
		s.include_children == true
		s.destination != ""
	}
}

# At least two distinct sources must appear in the central destination, with a
# dated query or report proving centralisation is working, not just configured
has_multi_source_evidence if {
	input.multi_source_log_evidence.source_count >= 2
	input.multi_source_log_evidence.query_timestamp != ""
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
			"sink_count": count(sinks),
			"destination_access_restricted": input.destination_access_restricted,
			"multi_source_log_evidence": input.multi_source_log_evidence,
			"requires_example_evidence": true,
		},
	}
}

# ---------------------------
# Message Logic
# ---------------------------
generate_message := msg if {
	not sinks_defined_at_scope
	msg := "FAIL: No org or folder-level sinks found with confirmed child resource coverage"
}

generate_message := msg if {
	sinks_defined_at_scope
	not input.destination_access_restricted
	msg := "FAIL: Access to the central logging destination is not restricted, allowing uncontrolled modification or deletion"
}

generate_message := msg if {
	input.destination_access_restricted
	not has_multi_source_evidence
	msg := "INCONCLUSIVE: No query or report found showing logs from multiple sources arriving centrally"
}

generate_message := msg if {
	compliant
	msg := "PASS: Sinks are centrally scoped with child coverage, destination access is restricted, and evidence confirms logs from multiple sources are centralised"
}

# ---------------------------
# Helper Functions
# ---------------------------
get_array(obj, key) := value if {
	value := obj[key]
} else := []
