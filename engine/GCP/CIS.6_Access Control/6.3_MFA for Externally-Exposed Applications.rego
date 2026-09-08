# METADATA
# title: Ensure MFA is required for externally exposed applications (GCP)
# description: |
#   All externally accessible applications must enforce MFA via a central identity provider
#   (Google Workspace / Cloud Identity) or via Identity-Aware Proxy (IAP) where applicable.
#   MFA enforcement must be consistent and verifiable via Cloud Audit Logs or sign-in logs.
# related_resources:
# - ref: https://cloud.google.com/iam/docs
#   description: GCP IAM Documentation
# - ref: https://cloud.google.com/iap/docs
#   description: Identity-Aware Proxy Documentation
# custom:
#   control_id: CIS-6.3
#   framework: cis
#   benchmark: gcp-foundations
#   version: v2.0.0
#   severity: high
#   service: IAM
#   requires_permissions:
#   - logging.viewer
#   - iap.viewer

package cis.gcp_foundations.v2_0_0.control_6_3

import rego.v1

default compliant := false

# ---------------------------
# Compliance Logic
# ---------------------------
compliant if {
  input.mfa_policy_enabled == true                 # MFA enforced via IdP
  input.sso_integration_enforced == true           # Google Workspace / Cloud Identity SSO or IAP
  input.externally_exposed_apps_covered == true    # All external apps protected
  has_valid_signin_event
}

# Validate at least one MFA-enforced sign-in event
has_valid_signin_event if {
  some e in input.signin_logs

  e.application != ""
  e.mfa_required == true
  e.timestamp != ""
}

# ---------------------------
# Result Output
# ---------------------------
result := {
  "compliant": compliant,
  "message": generate_message,
  "details": {
    "apps_covered": input.externally_exposed_apps_covered,
    "signin_log_count": count(input.signin_logs)
  }
}

# ---------------------------
# Message Logic
# ---------------------------
generate_message := "PASS: MFA enforced consistently for externally exposed GCP applications via IdP/IAP" if compliant

generate_message := "FAIL: MFA not consistently enforced for externally exposed applications" if not compliant