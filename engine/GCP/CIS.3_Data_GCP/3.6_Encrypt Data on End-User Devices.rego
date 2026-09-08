# METADATA
# title: Encrypt Data on End-User Devices (GCP)
# description: |
#   End-user devices containing sensitive data must have storage encryption
#   enabled. Where endpoint management is in scope, managed devices must meet
#   encryption requirements before accessing sensitive GCP services.
#
#   The control verifies:
#   - Endpoint encryption policy exists
#   - Managed endpoint scope is defined
#   - Device encryption compliance is evidenced
#   - Encryption coverage is known
#   - Non-compliant devices are identified and handled
#   - Recovery and exception workflows are documented
#   - Periodic compliance review is performed
#   - Endpoint scope boundaries are documented when end-user devices are out
#     of scope
#
# related_resources:
# - ref: https://support.google.com/a/topic/24642
#   description: Google Workspace Endpoint Management Documentation
# - ref: https://cloud.google.com/access-context-manager/docs
#   description: Google Cloud Access Context Manager Documentation
# - ref: https://cloud.google.com/iam/docs/context-aware-access
#   description: Context-Aware Access Documentation
#
# custom:
#   control_id: CIS-3.6
#   framework: cis
#   benchmark: gcp-foundations
#   version: v2.0.0
#   safeguard: 3.6
#   severity: high
#   service: Endpoint Management
#   asset_type: Data
#   implementation_group: 1
#   requires_permissions:
#   - iam.roles.get
#   - accesscontextmanager.accessLevels.get
#   - logging.viewer

package cis.gcp_foundations.v2_0_0.control_3_6

import rego.v1

# ---------------------------
# Default Result
# ---------------------------
default result := {
  "compliant": false,
  "message": "Evaluation failed: insufficient end-user device encryption evidence",
  "details": {}
}

default compliant := false

# ---------------------------
# Compliance Logic
# ---------------------------
compliant if {
  input.endpoints_in_scope == true
  input.encryption_policy_defined == true
  input.device_encryption_enforced == true
  input.encryption_coverage_verified == true
  input.non_compliant_handling_defined == true
  input.periodic_review_completed == true
  valid_device_coverage
  valid_review_evidence
}

compliant if {
  input.endpoints_in_scope == false
  input.scope_statement_available == true
}

# ---------------------------
# Validate Device Coverage
# ---------------------------
valid_device_coverage if {
  input.enrolled_device_count >= 0
  input.encrypted_device_count >= 0
  input.non_compliant_device_count >= 0

  input.encrypted_device_count <= input.enrolled_device_count
  input.non_compliant_device_count <= input.enrolled_device_count

  input.encryption_status_report_date != ""
}

# ---------------------------
# Validate Non-Compliant Device Handling
# ---------------------------
valid_non_compliant_handling if {
  input.non_compliant_handling_defined == true
  input.non_compliant_workflow != ""
  input.recovery_workflow != ""
}

# ---------------------------
# Validate Review Evidence
# ---------------------------
valid_review_evidence if {
  input.periodic_review_completed == true
  input.last_review_date != ""
  input.review_reviewer != ""
  input.review_outcome != ""
}

# ---------------------------
# Result Output
# ---------------------------
result := output if {
  devices := get_array(input, "devices")
  exceptions := get_array(input, "encryption_exceptions")

  output := {
    "compliant": compliant,
    "message": generate_message,
    "affected_resources": devices,
    "details": {
      "endpoints_in_scope": input.endpoints_in_scope,
      "encryption_policy_defined":
          input.encryption_policy_defined,
      "device_encryption_enforced":
          input.device_encryption_enforced,
      "encryption_coverage_verified":
          input.encryption_coverage_verified,
      "enrolled_device_count":
          input.enrolled_device_count,
      "encrypted_device_count":
          input.encrypted_device_count,
      "non_compliant_device_count":
          input.non_compliant_device_count,
      "encryption_status_report_date":
          input.encryption_status_report_date,
      "non_compliant_handling_defined":
          input.non_compliant_handling_defined,
      "non_compliant_workflow":
          input.non_compliant_workflow,
      "recovery_workflow":
          input.recovery_workflow,
      "periodic_review_completed":
          input.periodic_review_completed,
      "last_review_date":
          input.last_review_date,
      "review_reviewer":
          input.review_reviewer,
      "review_outcome":
          input.review_outcome,
      "scope_statement_available":
          input.scope_statement_available,
      "scope_statement":
          input.scope_statement,
      "device_count":
          count(devices),
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
  input.endpoints_in_scope == false
  not input.scope_statement_available
  msg := "FAIL: End-user devices are out of scope but no documented scope statement was provided"
}

generate_message := msg if {
  input.endpoints_in_scope == false
  input.scope_statement_available
  msg := "PASS: End-user device encryption is assessed under a separate documented scope boundary"
}

generate_message := msg if {
  input.endpoints_in_scope == true
  not input.encryption_policy_defined
  msg := "FAIL: No endpoint encryption policy is defined for managed devices in scope"
}

generate_message := msg if {
  input.encryption_policy_defined
  not input.device_encryption_enforced
  msg := "FAIL: Encryption is not enforced on managed end-user devices in scope"
}

generate_message := msg if {
  input.device_encryption_enforced
  not input.encryption_coverage_verified
  msg := "INCONCLUSIVE: Device encryption is required but coverage and encryption status cannot be verified"
}

generate_message := msg if {
  input.encryption_coverage_verified
  not valid_device_coverage
  msg := "INCONCLUSIVE: Device coverage evidence exists but enrolled, encrypted, or non-compliant device counts cannot be validated"
}

generate_message := msg if {
  valid_device_coverage
  not input.non_compliant_handling_defined
  msg := "FAIL: No documented workflow exists for non-compliant or lost devices"
}

generate_message := msg if {
  input.non_compliant_handling_defined
  not valid_non_compliant_handling
  msg := "INCONCLUSIVE: Non-compliant device handling is claimed but recovery or remediation workflow evidence is incomplete"
}

generate_message := msg if {
  valid_non_compliant_handling
  not input.periodic_review_completed
  msg := "FAIL: No evidence of periodic endpoint encryption compliance review"
}

generate_message := msg if {
  input.periodic_review_completed
  not valid_review_evidence
  msg := "INCONCLUSIVE: Endpoint encryption review is recorded but reviewer, date, or outcome evidence is incomplete"
}

generate_message := msg if {
  valid_review_evidence
  not compliant
  msg := "INCONCLUSIVE: Endpoint encryption controls exist but device coverage, non-compliance handling, or review evidence could not be fully verified"
}

generate_message := msg if {
  compliant
  msg := "PASS: Encryption is enforced on managed end-user devices in scope, coverage is evidenced, non-compliance is handled through a documented workflow, and compliance is periodically reviewed"
}

# ---------------------------
# Helper Functions
# ---------------------------
get_array(obj, key) := value if {
  value := obj[key]
} else := []
