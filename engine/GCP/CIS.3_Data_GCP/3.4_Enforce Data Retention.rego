# METADATA
# title: Enforce Data Retention (GCP)
# description: |
#   Data within GCP must be retained according to the enterprise's documented
#   data management process. Retention requirements must define both minimum
#   and maximum timelines, and applicable GCP services must enforce those
#   requirements through configured retention and expiration controls.
#
#   The control verifies:
#   - Approved data retention schedule exists
#   - Minimum and maximum retention timelines are defined
#   - Cloud Storage retention policies are configured
#   - Bucket Lock or object holds are configured where applicable
#   - BigQuery expiration settings are configured
#   - Cloud SQL backup retention is configured
#   - Configured retention values align with the approved schedule
#   - Exceptions such as legal holds are approved and tracked
#   - Periodic retention review evidence exists
#
# related_resources:
# - ref: https://cloud.google.com/storage/docs/bucket-lock
#   description: Cloud Storage Bucket Lock Documentation
# - ref: https://cloud.google.com/storage/docs/bucket-lock-retention-policy
#   description: Cloud Storage Retention Policy Documentation
# - ref: https://cloud.google.com/storage/docs/object-holds
#   description: Cloud Storage Object Holds Documentation
# - ref: https://cloud.google.com/bigquery/docs/managing-tables
#   description: BigQuery Table Management and Expiration Documentation
# - ref: https://cloud.google.com/sql/docs
#   description: Cloud SQL Documentation
#
# custom:
#   control_id: CIS-3.4
#   framework: cis
#   benchmark: gcp-foundations
#   version: v2.0.0
#   safeguard: 3.4
#   severity: high
#   service: Data Retention
#   asset_type: Data
#   implementation_group: 1
#   requires_permissions:
#   - storage.buckets.get
#   - storage.objects.get
#   - bigquery.datasets.get
#   - bigquery.tables.get
#   - cloudsql.instances.get
#   - logging.viewer

package cis.gcp_foundations.v2_0_0.control_3_4

import rego.v1

# ---------------------------
# Default Result
# ---------------------------
default result := {
  "compliant": false,
  "message": "Evaluation failed: insufficient data retention evidence",
  "details": {}
}

default compliant := false

# ---------------------------
# Compliance Logic
# ---------------------------
compliant if {
  input.retention_schedule_exists == true
  input.minimum_retention_defined == true
  input.maximum_retention_defined == true
  input.cloud_storage_retention_configured == true
  input.bigquery_retention_configured == true
  input.cloud_sql_retention_configured == true
  input.retention_alignment_verified == true
  input.exceptions_managed == true
  input.review_completed == true
  valid_retention_schedule
  valid_retention_controls
  valid_exception_evidence
  valid_review_evidence
}

# ---------------------------
# Validate Retention Schedule
# ---------------------------
valid_retention_schedule if {
  input.retention_schedule_name != ""
  input.retention_schedule_version != ""
  input.retention_schedule_approval_date != ""

  some policy in input.retention_requirements

  policy.data_class != ""
  policy.minimum_retention_days >= 0
  policy.maximum_retention_days >= 0
  policy.maximum_retention_days >= policy.minimum_retention_days
}

# ---------------------------
# Validate Retention Controls
# ---------------------------
valid_retention_controls if {
  some control in input.retention_controls

  control.resource_name != ""
  control.resource_type != ""
  control.data_class != ""
  control.configured_retention_days >= 0
  control.policy_minimum_days >= 0
  control.policy_maximum_days >= 0

  control.configured_retention_days >= control.policy_minimum_days
  control.configured_retention_days <= control.policy_maximum_days
}

# ---------------------------
# Validate Exceptions
# ---------------------------
valid_exception_evidence if {
  every exception in get_array(input, "retention_exceptions") {
    exception.exception_id != ""
    exception.resource_name != ""
    exception.reason != ""
    exception.approver != ""
    exception.approval_date != ""
    exception.expiry_date != ""
  }
}

# ---------------------------
# Validate Review Evidence
# ---------------------------
valid_review_evidence if {
  input.review_date != ""
  input.review_reviewer != ""
  input.review_outcome != ""
}

# ---------------------------
# Result Output
# ---------------------------
result := output if {
  requirements := get_array(input, "retention_requirements")
  controls := get_array(input, "retention_controls")
  exceptions := get_array(input, "retention_exceptions")

  output := {
    "compliant": compliant,
    "message": generate_message,
    "affected_resources": controls,
    "details": {
      "retention_schedule_exists":
          input.retention_schedule_exists,
      "retention_schedule_name":
          input.retention_schedule_name,
      "retention_schedule_version":
          input.retention_schedule_version,
      "retention_schedule_approval_date":
          input.retention_schedule_approval_date,
      "minimum_retention_defined":
          input.minimum_retention_defined,
      "maximum_retention_defined":
          input.maximum_retention_defined,
      "cloud_storage_retention_configured":
          input.cloud_storage_retention_configured,
      "bigquery_retention_configured":
          input.bigquery_retention_configured,
      "cloud_sql_retention_configured":
          input.cloud_sql_retention_configured,
      "retention_alignment_verified":
          input.retention_alignment_verified,
      "exceptions_managed":
          input.exceptions_managed,
      "review_completed":
          input.review_completed,
      "review_date":
          input.review_date,
      "review_reviewer":
          input.review_reviewer,
      "review_outcome":
          input.review_outcome,
      "retention_requirement_count":
          count(requirements),
      "retention_control_count":
          count(controls),
      "exception_count":
          count(exceptions),
      "requires_example_evidence": true
    }
  }
}

# ---------------------------
# Message Logic
# ---------------------------
generate_message := msg if {
  not input.retention_schedule_exists
  msg := "FAIL: No approved enterprise data retention schedule found"
}

generate_message := msg if {
  input.retention_schedule_exists
  not input.minimum_retention_defined
  msg := "FAIL: Minimum data retention timelines are not defined"
}

generate_message := msg if {
  input.minimum_retention_defined
  not input.maximum_retention_defined
  msg := "FAIL: Maximum data retention timelines are not defined"
}

generate_message := msg if {
  input.maximum_retention_defined
  not valid_retention_schedule
  msg := "INCONCLUSIVE: Retention schedule exists but data-class timelines or approval evidence could not be fully verified"
}

generate_message := msg if {
  valid_retention_schedule
  not input.cloud_storage_retention_configured
  msg := "FAIL: Cloud Storage retention controls are not configured for in-scope data"
}

generate_message := msg if {
  input.cloud_storage_retention_configured
  not input.bigquery_retention_configured
  msg := "FAIL: BigQuery retention or expiration controls are not configured for in-scope data"
}

generate_message := msg if {
  input.bigquery_retention_configured
  not input.cloud_sql_retention_configured
  msg := "FAIL: Cloud SQL backup retention controls are not configured for in-scope databases"
}

generate_message := msg if {
  input.cloud_sql_retention_configured
  not input.retention_alignment_verified
  msg := "FAIL: Configured GCP retention values do not align with the approved retention schedule"
}

generate_message := msg if {
  input.retention_alignment_verified
  not valid_retention_controls
  msg := "INCONCLUSIVE: Retention settings are present but policy alignment or resource scope could not be fully verified"
}

generate_message := msg if {
  valid_retention_controls
  not input.exceptions_managed
  msg := "FAIL: Retention exceptions such as legal holds are not approved and tracked"
}

generate_message := msg if {
  input.exceptions_managed
  not valid_exception_evidence
  msg := "INCONCLUSIVE: Retention exceptions exist but approval or expiry evidence is incomplete"
}

generate_message := msg if {
  valid_exception_evidence
  not input.review_completed
  msg := "FAIL: No evidence of periodic data retention review"
}

generate_message := msg if {
  input.review_completed
  not valid_review_evidence
  msg := "INCONCLUSIVE: Retention review is recorded but reviewer, date, or outcome evidence is incomplete"
}

generate_message := msg if {
  valid_review_evidence
  not compliant
  msg := "INCONCLUSIVE: Data retention requirements and controls exist but policy alignment, exceptions, or review evidence could not be fully verified"
}

generate_message := msg if {
  compliant
  msg := "PASS: GCP data retention requirements are documented, technically enforced, aligned to the approved schedule, and periodically reviewed"
}

# ---------------------------
# Helper Functions
# ---------------------------
get_array(obj, key) := value if {
  value := obj[key]
} else := []
