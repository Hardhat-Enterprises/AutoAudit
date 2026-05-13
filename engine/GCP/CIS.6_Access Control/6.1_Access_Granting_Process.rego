# METADATA
# title: Ensure access granting process is documented and enforced (GCP)
# description: |
#   Access to GCP resources must follow a documented, repeatable, and auditable process.
#   Access should be requested through an approved workflow, reviewed by designated approvers,
#   and provisioned using IAM roles and groups instead of direct user bindings where possible.
#   Each request must include justification, approval, and timestamps, and must be traceable
#   to a corresponding IAM policy change and Cloud Audit Logs entry.
# related_resources:
# - ref: https://cloud.google.com/iam/docs
#   description: GCP IAM Documentation
# - ref: https://cloud.google.com/logging/docs/audit
#   description: Cloud Audit Logs Overview
# custom:
#   control_id: CIS-6.1
#   framework: cis
#   benchmark: gcp-foundations
#   version: v2.0.0
#   severity: high
#   service: IAM
#   requires_permissions:
#   - logging.viewer
#   - iam.securityReviewer

package cis.gcp_foundations.v2_0_0.control_6_1

import rego.v1

# Default result
default result := {
  "compliant": false,
  "message": "Evaluation failed: insufficient data to verify access granting process",
  "details": {}
}

default compliant := false

# ---------------------------
# Compliance Logic
# ---------------------------
compliant if {
  input.process_documented == true
  input.workflow_enforced == true
  input.role_based_access == true   # IAM roles / Google Groups
  input.audit_logging_enabled == true  # Cloud Audit Logs enabled
  has_valid_request
}

# Ensure at least one complete, auditable request exists
has_valid_request if {
  some req in input.access_requests

  req.request_id != ""
  req.requester != ""
  req.approver != ""
  req.role != ""              # IAM role (e.g., roles/viewer)
  req.group != ""             # Google Group or IAM binding target
  req.justification != ""

  req.request_timestamp != ""
  req.approval_timestamp != ""
  req.provisioning_timestamp != ""

  req.audit_log_matched == true   # Matches Cloud Audit Logs entry
}

# ---------------------------
# Result Output
# ---------------------------
result := output if {
  requests := get_array(input, "access_requests")

  output := {
    "compliant": compliant,
    "message": generate_message,
    "affected_resources": requests,
    "details": {
      "process_documented": input.process_documented,
      "workflow_enforced": input.workflow_enforced,
      "role_based_access": input.role_based_access,
      "audit_logging_enabled": input.audit_logging_enabled,
      "request_count": count(requests),
      "requires_example_evidence": true
    }
  }
}

# ---------------------------
# Message Logic
# ---------------------------
generate_message := msg if {
  not input.process_documented
  msg := "FAIL: No documented access granting process found"
}

generate_message := msg if {
  input.process_documented
  not input.workflow_enforced
  msg := "FAIL: Access requests are not processed through an approved workflow"
}

generate_message := msg if {
  input.workflow_enforced
  not input.role_based_access
  msg := "FAIL: Access is not granted via IAM roles or groups"
}

generate_message := msg if {
  input.role_based_access
  not input.audit_logging_enabled
  msg := "FAIL: Cloud Audit Logs for IAM changes are not enabled"
}

generate_message := msg if {
  input.audit_logging_enabled
  not has_valid_request
  msg := "INCONCLUSIVE: No complete access request with approval and audit log linkage found"
}

generate_message := msg if {
  compliant
  msg := "PASS: Access granting process is documented, enforced, and supported by auditable GCP IAM evidence"
}

# ---------------------------
# Helper Functions
# ---------------------------
get_array(obj, key) := value if {
  value := obj[key]
} else := []