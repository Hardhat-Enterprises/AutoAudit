# METADATA
# title: Ensure access revocation process is documented and enforced (GCP)
# description: |
#   Access to GCP resources must be revoked in a timely and auditable manner
#   upon user termination or role change. Accounts should be suspended (not deleted)
#   via the identity provider (e.g., Google Workspace or Cloud Identity) to preserve audit trails,
#   and all access (IAM roles, group memberships, active sessions) must be removed promptly.
#   Each revocation must be traceable to an approved workflow and corresponding Cloud Audit Logs evidence.
# related_resources:
# - ref: https://cloud.google.com/iam/docs
#   description: GCP IAM Documentation
# - ref: https://cloud.google.com/logging/docs/audit
#   description: Cloud Audit Logs Overview
# custom:
#   control_id: CIS-6.2
#   framework: cis
#   benchmark: gcp-foundations
#   version: v2.0.0
#   severity: high
#   service: IAM
#   requires_permissions:
#   - logging.viewer
#   - iam.securityReviewer

package cis.gcp_foundations.v2_0_0.control_6_2

import rego.v1

# ---------------------------
# Default Values
# ---------------------------
default result := {
  "compliant": false,
  "message": "Evaluation failed: insufficient data to verify access revocation process",
  "details": {}
}

default compliant := false

# ---------------------------
# Compliance Logic
# ---------------------------
compliant if {
  input.process_documented == true
  input.revocation_workflow_enforced == true
  input.account_suspension_enabled == true   # via Google Workspace / Cloud Identity
  input.access_removal_enforced == true      # IAM roles + group memberships removed
  input.audit_logging_enabled == true        # Cloud Audit Logs enabled
  has_valid_revocation
}

# Ensure at least one complete revocation example exists
has_valid_revocation if {
  some req in input.revocation_events

  req.user_id != ""
  req.event_type != ""        # termination or role_change
  req.initiator != ""         # HR system / manager / ticket
  req.actioned_by != ""

  req.event_timestamp != ""
  req.suspension_timestamp != ""

  # Ensure access removal evidence exists (IAM roles or Google Groups)
  count(req.removed_groups) > 0 or count(req.removed_roles) > 0

  req.audit_log_matched == true   # Matches Cloud Audit Logs entry
}

# ---------------------------
# Result Output
# ---------------------------
result := output if {
  events := get_array(input, "revocation_events")

  output := {
    "compliant": compliant,
    "message": generate_message,
    "affected_resources": events,
    "details": {
      "process_documented": input.process_documented,
      "revocation_workflow_enforced": input.revocation_workflow_enforced,
      "account_suspension_enabled": input.account_suspension_enabled,
      "access_removal_enforced": input.access_removal_enforced,
      "audit_logging_enabled": input.audit_logging_enabled,
      "event_count": count(events),
      "requires_example_evidence": true
    }
  }
}

# ---------------------------
# Message Logic
# ---------------------------
generate_message := msg if {
  not input.process_documented
  msg := "FAIL: No documented access revocation (offboarding) process found"
}

generate_message := msg if {
  input.process_documented
  not input.revocation_workflow_enforced
  msg := "FAIL: Revocation is not enforced through a defined workflow (HR/ticketing)"
}

generate_message := msg if {
  input.revocation_workflow_enforced
  not input.account_suspension_enabled
  msg := "FAIL: Accounts are not suspended via identity provider upon termination or role change"
}

generate_message := msg if {
  input.account_suspension_enabled
  not input.access_removal_enforced
  msg := "FAIL: Access (IAM roles/groups) is not consistently removed during revocation"
}

generate_message := msg if {
  input.access_removal_enforced
  not input.audit_logging_enabled
  msg := "FAIL: Cloud Audit Logs for revocation actions are not enabled"
}

generate_message := msg if {
  input.audit_logging_enabled
  not has_valid_revocation
  msg := "INCONCLUSIVE: No complete revocation example with matching audit logs found"
}

generate_message := msg if {
  compliant
  msg := "PASS: Access revocation is documented, enforced, and supported by auditable GCP IAM evidence"
}

# ---------------------------
# Helper Functions
# ---------------------------
get_array(obj, key) := value if {
  value := obj[key]
} else := []