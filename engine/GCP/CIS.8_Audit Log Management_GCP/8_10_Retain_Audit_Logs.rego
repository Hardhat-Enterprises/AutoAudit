# METADATA
# title: Retain Audit Logs (GCP)
# description: |
#   Organisations must retain audit logs across enterprise assets for a minimum of 90 days.
#   Logging bucket retention should be set to at least 90 days for in-scope audit logs. Where
#   immutability is required, logs should be exported to Cloud Storage with a retention policy and
#   retention lock so they cannot be shortened or deleted early. Retention must be validated by
#   demonstrating that logs older than 90 days remain available for a key service.
# related_resources:
# - ref: https://cloud.google.com/logging/docs/buckets#retention
#   description: Logging Bucket Retention Documentation
# - ref: https://cloud.google.com/storage/docs/bucket-lock
#   description: Cloud Storage Retention Policy and Retention Lock Documentation
# custom:
#   control_id: CIS-8.10
#   framework: cis
#   benchmark: gcp-foundations
#   version: v2.0.0
#   severity: medium
#   service: Cloud Logging / Cloud Storage
#   requires_permissions:
#   - logging.buckets.list
#   - storage.buckets.getRetentionPolicy
#   - logging.logEntries.list

package cis.gcp_foundations.v2_0_0.control_8_10

import rego.v1

# Default result
default result := {
	"compliant": false,
	"message": "Evaluation failed: insufficient data to verify audit log retention",
	"details": {},
}

default compliant := false

# ---------------------------
# Compliance Logic
# ---------------------------
compliant if {
	has_adequate_retention
	archive_retention_lock_confirmed
	has_retrieval_evidence
}

# Every logging bucket in scope must meet or exceed the 90-day minimum -
# one under-retained bucket means audit logs could be lost before the required window
has_adequate_retention if {
	count(input.logging_buckets) > 0
	every b in input.logging_buckets {
		b.retention_days >= 90
	}
}

# If a Cloud Storage archive is in use, its retention policy and retention lock
# must be confirmed enabled so logs can't be shortened or deleted early.
# If no archive is used, this requirement doesn't apply
archive_retention_lock_confirmed if {
	input.storage_archive_used == false
}

archive_retention_lock_confirmed if {
	input.storage_archive_used == true
	input.storage_archive.retention_lock_enabled == true
}

# A dated query must prove a record older than 90 days is still retrievable --
# configured retention alone doesn't confirm logs are actually preserved in practice
has_retrieval_evidence if {
	input.retrieval_evidence.query_timestamp != ""
	input.retrieval_evidence.oldest_record_age_days >= 90
}

# ---------------------------
# Result Output
# ---------------------------
result := output if {
	logging_buckets := get_array(input, "logging_buckets")

	output := {
		"compliant": compliant,
		"message": generate_message,
		"affected_resources": logging_buckets,
		"details": {
			"logging_bucket_count": count(logging_buckets),
			"storage_archive_used": input.storage_archive_used,
			"storage_archive": input.storage_archive,
			"retrieval_evidence": input.retrieval_evidence,
			"requires_example_evidence": true,
		},
	}
}

# ---------------------------
# Message Logic
# ---------------------------
generate_message := msg if {
	count(input.logging_buckets) == 0
	msg := "INCONCLUSIVE: No logging bucket retention configuration was provided to verify against the 90-day minimum"
}

generate_message := msg if {
	count(input.logging_buckets) > 0
	not has_adequate_retention
	msg := "FAIL: One or more logging buckets have retention configured below the 90-day minimum"
}

generate_message := msg if {
	has_adequate_retention
	not archive_retention_lock_confirmed
	msg := "FAIL: Cloud Storage archive retention policy and retention lock are not confirmed"
}

generate_message := msg if {
	archive_retention_lock_confirmed
	not has_retrieval_evidence
	msg := "FAIL: No evidence found proving audit logs older than 90 days remain accessible"
}

generate_message := msg if {
	compliant
	msg := "PASS: Retention meets or exceeds 90 days and retrieval evidence confirms logs older than 90 days remain accessible"
}

# ---------------------------
# Helper Functions
# ---------------------------
get_array(obj, key) := value if {
	value := obj[key]
} else := []
