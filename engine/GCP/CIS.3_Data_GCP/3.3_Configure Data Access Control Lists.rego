# METADATA
# title: Configure Data Access Control Lists (GCP)
# description: |
#   Access to data within GCP must be controlled according to the user's need
#   to know. Data access permissions must be appropriately restricted across
#   Cloud Storage, BigQuery, and Cloud SQL, with privileged access controlled
#   and access reviews performed periodically.
#
#   The control verifies:
#   - Data access controls are configured
#   - Least privilege is applied to sensitive data stores
#   - Access is predominantly group-based
#   - Privileged roles and break-glass access are controlled
#   - Public access is prevented for sensitive storage
#   - Access review evidence exists
#   - Access review outcomes are documented
#   - Access reports can identify principals with access to sensitive stores
#
# related_resources:
# - ref: https://cloud.google.com/iam/docs
#   description: Google Cloud IAM Documentation
# - ref: https://cloud.google.com/storage/docs/access-control
#   description: Cloud Storage Access Control Documentation
# - ref: https://cloud.google.com/bigquery/docs/access-control
#   description: BigQuery Access Control Documentation
# - ref: https://cloud.google.com/sql/docs
#   description: Cloud SQL Documentation
# - ref: https://cloud.google.com/logging/docs/audit
#   description: Cloud Audit Logs Overview
#
# custom:
#   control_id: CIS-3.3
#   framework: cis
#   benchmark: gcp-foundations
#   version: v2.0.0
#   safeguard: 3.3
#   severity: high
#   service: IAM
#   asset_type: Data
#   implementation_group: 1
#   requires_permissions:
#   - resourcemanager.projects.getIamPolicy
#   - storage.buckets.getIamPolicy
#   - storage.objects.getIamPolicy
#   - bigquery.datasets.getIamPolicy
#   - bigquery.tables.getIamPolicy
#   - cloudsql.instances.get
#   - logging.viewer

package cis.gcp_foundations.v2_0_0.control_3_3

import rego.v1

# ---------------------------
# Default Result
# ---------------------------
default result := {
  "compliant": false,
  "message": "Evaluation failed: insufficient data access control evidence",
  "details": {}
}

default compliant := false

# ---------------------------
# Compliance Logic
# ---------------------------
compliant if {
  input.access_controls_configured == true
  input.least_privilege_enforced == true
  input.group_based_access == true
  input.privileged_access_controlled == true
  input.public_access_prevented == true
  input.access_report_available == true
  input.access_review_completed == true
  valid_sensitive_store
  valid_access_review
}

# ---------------------------
# Validate Sensitive Data Store
# ---------------------------
valid_sensitive_store if {
  input.sensitive_store.name != ""
  input.sensitive_store.type != ""
  input.sensitive_store.scope != ""
}

# ---------------------------
# Validate Access Principals
# ---------------------------
valid_access_principals if {
  some principal in input.access_principals

  principal.principal != ""
  principal.principal_type != ""
  principal.role != ""
  principal.access_scope != ""
}

# ---------------------------
# Validate Public Access
# ---------------------------
public_access_verified if {
  input.public_access_prevented == true
  input.public_access_status != ""
}

# ---------------------------
# Validate Privileged Access
# ---------------------------
privileged_access_verified if {
  input.privileged_access_controlled == true
  input.privileged_roles_documented == true
  input.break_glass_documented == true
}

# ---------------------------
# Validate Access Review Evidence
# ---------------------------
valid_access_review if {
  input.access_review_completed == true
  input.access_review_date != ""
  input.access_review_reviewer != ""
  input.access_review_outcome != ""
}

# ---------------------------
# Result Output
# ---------------------------
result := output if {
  principals := get_array(input, "access_principals")
  sensitive_stores := get_array(input, "sensitive_stores")
  exceptions := get_array(input, "access_exceptions")

  output := {
    "compliant": compliant,
    "message": generate_message,
    "affected_resources": sensitive_stores,
    "details": {
      "access_controls_configured": input.access_controls_configured,
      "least_privilege_enforced": input.least_privilege_enforced,
      "group_based_access": input.group_based_access,
      "privileged_access_controlled":
          input.privileged_access_controlled,
      "privileged_roles_documented":
          input.privileged_roles_documented,
      "break_glass_documented":
          input.break_glass_documented,
      "public_access_prevented":
          input.public_access_prevented,
      "public_access_status":
          input.public_access_status,
      "access_report_available":
          input.access_report_available,
      "sensitive_store":
          input.sensitive_store,
      "access_principal_count":
          count(principals),
      "sensitive_store_count":
          count(sensitive_stores),
      "access_exception_count":
          count(exceptions),
      "access_review_completed":
          input.access_review_completed,
      "access_review_date":
          input.access_review_date,
      "access_review_reviewer":
          input.access_review_reviewer,
      "access_review_outcome":
          input.access_review_outcome,
      "requires_example_evidence": true
    }
  }
}

# ---------------------------
# Message Logic
# ---------------------------
generate_message := msg if {
  not input.access_controls_configured
  msg := "FAIL: Data access controls are not configured for in-scope GCP data stores"
}

generate_message := msg if {
  input.access_controls_configured
  not input.least_privilege_enforced
  msg := "FAIL: Least privilege or need-to-know access is not enforced"
}

generate_message := msg if {
  input.least_privilege_enforced
  not input.group_based_access
  msg := "FAIL: Data access is not predominantly controlled through groups or appropriately scoped principals"
}

generate_message := msg if {
  input.group_based_access
  not input.privileged_access_controlled
  msg := "FAIL: Privileged access to sensitive data stores is not adequately controlled"
}

generate_message := msg if {
  input.privileged_access_controlled
  not privileged_access_verified
  msg := "INCONCLUSIVE: Privileged access is claimed but role constraints or break-glass handling evidence is incomplete"
}

generate_message := msg if {
  privileged_access_verified
  not input.public_access_prevented
  msg := "FAIL: Public access is not prevented for in-scope sensitive data stores"
}

generate_message := msg if {
  input.public_access_prevented
  not public_access_verified
  msg := "INCONCLUSIVE: Public access prevention is claimed but supporting configuration evidence is missing"
}

generate_message := msg if {
  public_access_verified
  not input.access_report_available
  msg := "FAIL: No access report identifying principals with access to sensitive data stores is available"
}

generate_message := msg if {
  input.access_report_available
  not valid_access_principals
  msg := "INCONCLUSIVE: Access report exists but principals, roles, or access scope cannot be clearly verified"
}

generate_message := msg if {
  valid_access_principals
  not valid_sensitive_store
  msg := "INCONCLUSIVE: Sensitive data store scope is not clearly identified for access review"
}

generate_message := msg if {
  valid_sensitive_store
  not input.access_review_completed
  msg := "FAIL: No evidence of a periodic access review for sensitive data stores"
}

generate_message := msg if {
  input.access_review_completed
  not valid_access_review
  msg := "INCONCLUSIVE: Access review is recorded but reviewer, date, or review outcome evidence is incomplete"
}

generate_message := msg if {
  valid_access_review
  not compliant
  msg := "INCONCLUSIVE: Data access controls exist but least privilege, privileged access, public access prevention, or review evidence could not be fully verified"
}

generate_message := msg if {
  compliant
  msg := "PASS: GCP data access controls enforce least privilege and need-to-know access, restrict privileged and public access, and are periodically reviewed"
}

# ---------------------------
# Helper Functions
# ---------------------------
get_array(obj, key) := value if {
  value := obj[key]
} else := []
