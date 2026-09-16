# METADATA
# title: Establish and Maintain a Data Management Process (GCP)
# description: |
#   Data within GCP must be governed through a documented and approved data
#   management process. The process must address data sensitivity, ownership,
#   handling requirements, retention limits, and disposal requirements.
#
#   The control verifies:
#   - Data management process is documented and approved
#   - Data sensitivity and classification requirements are defined
#   - Data owners or stewards are assigned
#   - Data handling, retention, and disposal requirements are defined
#   - GCP implementation evidence exists
#   - Process scope is defined
#   - Annual or significant-change review evidence exists
#
# related_resources:
# - ref: https://cloud.google.com/dataplex/docs
#   description: Google Cloud Dataplex Documentation
# - ref: https://cloud.google.com/sensitive-data-protection/docs
#   description: Sensitive Data Protection Documentation
# - ref: https://cloud.google.com/storage/docs
#   description: Cloud Storage Documentation
# - ref: https://cloud.google.com/bigquery/docs
#   description: BigQuery Documentation
# - ref: https://cloud.google.com/sql/docs
#   description: Cloud SQL Documentation
# - ref: https://cloud.google.com/kms/docs
#   description: Cloud Key Management Service Documentation
# - ref: https://cloud.google.com/logging/docs/audit
#   description: Cloud Audit Logs Overview
#
# custom:
#   control_id: CIS-3.1
#   framework: cis
#   benchmark: gcp-foundations
#   version: v2.0.0
#   safeguard: 3.1
#   severity: high
#   service: Data Management
#   asset_type: Data
#   implementation_group: 1
#   requires_permissions:
#   - dataplex.catalogs.get
#   - dataplex.entries.get
#   - dlp.inspectTemplates.get
#   - dlp.jobs.get
#   - storage.buckets.get
#   - bigquery.datasets.get
#   - cloudsql.instances.get
#   - cloudkms.cryptoKeys.get
#   - logging.viewer

package cis.gcp_foundations.v2_0_0.control_3_1

import rego.v1

# ---------------------------
# Default Result
# ---------------------------
default result := {
  "compliant": false,
  "message": "Evaluation failed: insufficient data management process evidence",
  "details": {}
}

default compliant := false

# ---------------------------
# Compliance Logic
# ---------------------------
compliant if {
  input.process_documented == true
  input.process_approved == true
  input.data_sensitivity_defined == true
  input.data_owners_defined == true
  input.data_handling_requirements_defined == true
  input.data_retention_requirements_defined == true
  input.data_disposal_requirements_defined == true
  input.gcp_implementation_evidence == true
  input.scope_defined == true
  input.review_completed == true
  valid_data_owners
  valid_gcp_implementation
  valid_review_evidence
}

# ---------------------------
# Validate Data Owners
# ---------------------------
valid_data_owners if {
  some owner in input.data_owners

  owner.name != ""
  owner.domain != ""
  owner.role != ""
}

# ---------------------------
# Validate GCP Implementation
# ---------------------------
valid_gcp_implementation if {
  input.implementation.dataplex == true
}

valid_gcp_implementation if {
  input.implementation.cloud_dlp == true
}

valid_gcp_implementation if {
  input.implementation.cloud_storage == true
}

valid_gcp_implementation if {
  input.implementation.bigquery == true
}

valid_gcp_implementation if {
  input.implementation.cloud_sql == true
}

valid_gcp_implementation if {
  input.implementation.cloud_kms == true
}

valid_gcp_implementation if {
  input.implementation.cloud_audit_logs == true
}

valid_gcp_implementation if {
  input.implementation.policy_exports == true
}

# ---------------------------
# Validate Review Evidence
# ---------------------------
valid_review_evidence if {
  input.review_date != ""
  input.review_approver != ""

  (
    input.review_within_annual_cycle == true
    or
    input.review_triggered_by_significant_change == true
  )
}

# ---------------------------
# Result Output
# ---------------------------
result := output if {
  owners := get_array(input, "data_owners")
  environments := get_array(input, "covered_environments")
  exclusions := get_array(input, "exclusions")

  output := {
    "compliant": compliant,
    "message": generate_message,
    "affected_resources": {
      "data_owners": owners,
      "covered_environments": environments,
      "exclusions": exclusions
    },
    "details": {
      "process_documented": input.process_documented,
      "process_approved": input.process_approved,
      "data_sensitivity_defined": input.data_sensitivity_defined,
      "data_owners_defined": input.data_owners_defined,
      "data_handling_requirements_defined":
          input.data_handling_requirements_defined,
      "data_retention_requirements_defined":
          input.data_retention_requirements_defined,
      "data_disposal_requirements_defined":
          input.data_disposal_requirements_defined,
      "gcp_implementation_evidence":
          input.gcp_implementation_evidence,
      "scope_defined": input.scope_defined,
      "review_completed": input.review_completed,
      "review_date": input.review_date,
      "review_approver": input.review_approver,
      "review_within_annual_cycle":
          input.review_within_annual_cycle,
      "review_triggered_by_significant_change":
          input.review_triggered_by_significant_change,
      "implementation": input.implementation,
      "owner_count": count(owners),
      "environment_count": count(environments),
      "exclusion_count": count(exclusions),
      "requires_example_evidence": true
    }
  }
}

# ---------------------------
# Message Logic
# ---------------------------
generate_message := msg if {
  not input.process_documented
  msg := "FAIL: No documented data management process found"
}

generate_message := msg if {
  input.process_documented
  not input.process_approved
  msg := "FAIL: Data management process exists but approval evidence is missing"
}

generate_message := msg if {
  input.process_approved
  not input.data_sensitivity_defined
  msg := "FAIL: Data sensitivity or classification requirements are not defined"
}

generate_message := msg if {
  input.data_sensitivity_defined
  not input.data_owners_defined
  msg := "FAIL: Named data owners or stewards are not defined"
}

generate_message := msg if {
  input.data_owners_defined
  not input.data_handling_requirements_defined
  msg := "FAIL: Data handling requirements are not defined"
}

generate_message := msg if {
  input.data_handling_requirements_defined
  not input.data_retention_requirements_defined
  msg := "FAIL: Data retention requirements are not defined"
}

generate_message := msg if {
  input.data_retention_requirements_defined
  not input.data_disposal_requirements_defined
  msg := "FAIL: Data disposal requirements are not defined"
}

generate_message := msg if {
  input.data_disposal_requirements_defined
  not input.scope_defined
  msg := "FAIL: Data management process scope is not defined"
}

generate_message := msg if {
  input.scope_defined
  not input.gcp_implementation_evidence
  msg := "FAIL: No evidence that the data management process is implemented in GCP"
}

generate_message := msg if {
  input.gcp_implementation_evidence
  not valid_gcp_implementation
  msg := "INCONCLUSIVE: GCP implementation is claimed but no supporting implementation evidence was provided"
}

generate_message := msg if {
  valid_gcp_implementation
  not valid_data_owners
  msg := "INCONCLUSIVE: Data owners are defined but complete owner assignment evidence is missing"
}

generate_message := msg if {
  valid_data_owners
  not input.review_completed
  msg := "FAIL: No evidence of an annual or significant-change data management review"
}

generate_message := msg if {
  input.review_completed
  not valid_review_evidence
  msg := "INCONCLUSIVE: Review is recorded but review date, approver, or review cadence evidence is incomplete"
}

generate_message := msg if {
  input.review_completed
  valid_review_evidence
  not compliant
  msg := "INCONCLUSIVE: Data management governance and GCP implementation evidence are incomplete"
}

generate_message := msg if {
  compliant
  msg := "PASS: GCP data management process is documented, approved, implemented, and periodically reviewed"
}

# ---------------------------
# Helper Functions
# ---------------------------
get_array(obj, key) := value if {
  value := obj[key]
} else := []
