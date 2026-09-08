# METADATA
# title: Ensure MFA is required for administrative access (GCP)
# description: |
#   All administrative identities in GCP must enforce MFA using strong authentication
#   methods via Google Workspace or Cloud Identity. Privileged roles (e.g., Owner, Editor,
#   IAM Admin) must be clearly defined and monitored through Cloud Audit Logs.
# related_resources:
# - ref: https://cloud.google.com/iam/docs
#   description: GCP IAM Documentation
# - ref: https://cloud.google.com/logging/docs/audit
#   description: Cloud Audit Logs Overview
# custom:
#   control_id: CIS-6.5
#   framework: cis
#   benchmark: gcp-foundations
#   version: v2.0.0
#   severity: critical
#   service: IAM
#   requires_permissions:
#   - logging.viewer
#   - iam.securityReviewer

package cis.gcp_foundations.v2_0_0.control_6_5

import rego.v1

default compliant := false

# ---------------------------
# Compliance Logic
# ---------------------------
compliant if {
  input.admin_mfa_enabled == true        # MFA enforced for admin identities via IdP
  input.admin_scope_defined == true      # Privileged roles clearly identified
  has_admin_event
}

# Validate at least one admin activity with MFA
has_admin_event if {
  some e in input.admin_logs

  e.mfa_used == true
  e.timestamp != ""
}

# ---------------------------
# Result Output
# ---------------------------
result := {
  "compliant": compliant,
  "message": generate_message,
  "details": {
    "admin_count": count(input.admin_identities),
    "log_events": count(input.admin_logs)
  }
}

# ---------------------------
# Message Logic
# ---------------------------
generate_message := "PASS: MFA enforced for all GCP administrative access and validated via audit logs" if compliant

generate_message := "FAIL: Administrative access in GCP is not fully protected by MFA" if not compliant