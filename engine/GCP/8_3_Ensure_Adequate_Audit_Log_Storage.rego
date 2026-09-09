A
# METADATA
# title: Ensure Adequate Audit Log Storage (GCP)
# description: |
#   Organisations must ensure that logging destinations maintain adequate storage to comply with the
#   enterprise's audit log management process.
#   Logging destinations should be sized and configured so exports do not fail and retention targets can
#   be met, using Logging bucket retention, BigQuery dataset settings, or Cloud Storage lifecycle and
#   retention controls as appropriate. Export errors and quota or capacity signals must be monitored so
#   drops in log collection are detected quickly.
# related_resources:
# - ref: https://cloud.google.com/logging/docs/buckets
#   description: Logging Bucket Retention Documentation
# - ref: https://cloud.google.com/storage/docs/bucket-lock
#   description: Cloud Storage Retention Policy Documentation
# custom:
#   control_id: CIS-8.3
#   framework: cis
#   benchmark: gcp-foundations
#   version: v2.0.0
#   severity: medium
#   service: Cloud Logging / BigQuery / Cloud Storage
#   requires_permissions:
#   - logging.buckets.list
#   - bigquery.datasets.get
#   - storage.buckets.getObjectRetention
#   - monitoring.alertPolicies.list

package cis.gcp_foundations.v2_0_0.control_8_3

import rego.v1

# Default result
default result := {
	"compliant": false,
	"message": "Evaluation failed: insufficient data to verify audit log storage adequacy",
	"details": {},
}

default compliant := false

# ---------------------------
# Compliance Logic
# ---------------------------
compliant if {
	has_defined_retention
	input.monitoring_configured == true
	has_monitoring_evidence
}

# Every logging destination in use must have retention explicitly configured -
# an undefined or unconfigured destination can't reliably meet the retention target
has_defined_retention if {
	count(input.destinations) > 0
	every destination in input.destinations {
		destination.retention_configured == true
		destination.retention_days > 0
	}
}

# A time-stamped artefact (alert, report, or dashboard snapshot) must show export
# health and capacity monitoring is actually active, not just configured on paper
has_monitoring_evidence if {
	input.monitoring_evidence_date != ""
	input.monitoring_evidence_type != ""
}

# ---------------------------
# Result Output
# ---------------------------
result := output if {
	destinations := get_array(input, "destinations")

	output := {
		"compliant": compliant,
		"message": generate_message,
		"affected_resources": destinations,
		"details": {
			"destination_count": count(destinations),
			"monitoring_configured": input.monitoring_configured,
			"monitoring_evidence_date": input.monitoring_evidence_date,
			"monitoring_evidence_type": input.monitoring_evidence_type,
			"requires_example_evidence": true,
		},
	}
}

# ---------------------------
# Message Logic
# ---------------------------
generate_message := msg if {
	not has_defined_retention
	msg := "FAIL: One or more logging destinations do not have retention explicitly configured"
}

generate_message := msg if {
	has_defined_retention
	not input.monitoring_configured
	msg := "FAIL: Export health and capacity monitoring is not configured for logging destinations"
}

generate_message := msg if {
	input.monitoring_configured
	not has_monitoring_evidence
	msg := "INCONCLUSIVE: No time-stamped artefact found showing monitoring is actively running"
}

generate_message := msg if {
	compliant
	msg := "PASS: Logging destinations have defined retention aligned with the standard, and export health and capacity monitoring is active"
}

# ---------------------------
# Helper Functions
# ---------------------------
get_array(obj, key) := value if {
	value := obj[key]
} else := []
