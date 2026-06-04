# METADATA
# title: Ensure MFA is required for remote network access (GCP)
# description: |
#   Remote access to GCP resources must be protected via MFA using centralized identity controls
#   (Google Workspace / Cloud Identity). Access paths should be brokered through Identity-Aware Proxy (IAP),
#   BeyondCorp Enterprise, or equivalent zero-trust controls. Enforcement must be verifiable via logs.
# related_resources:
# - ref: https://cloud.google.com/iap/docs
#   description: Identity-Aware Proxy Documentation
# - ref: https://cloud.google.com/beyondcorp-enterprise/docs
#   description: BeyondCorp Enterprise Overview
# custom:
#   control_id: CIS-6.4
#   framework: cis
#   benchmark: gcp-foundations
#   version: v2.0.0
#   severity: high
#   service: IAM
#   requires_permissions:
#   - logging.viewer
#   - iap.viewer

package cis.gcp_foundations.v2_0_0.control_6_4

import rego.v1

default compliant := false

# ---------------------------
# Compliance Logic
# ---------------------------
compliant if {
  input.remote_access_protected == true        # Access via IAP / BeyondCorp / secure proxy
  input.mfa_required_for_remote == true        # MFA enforced via IdP
  input.policy_applied == true                 # Access policy configured and active
  has_remote_event
}

# Validate at least one MFA-protected remote access event
has_remote_event if {
  some e in input.remote_access_logs

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
    "remote_events": count(input.remote_access_logs)
  }
}

# ---------------------------
# Message Logic
# ---------------------------
generate_message := "PASS: Remote access to GCP resources requires MFA and is enforced via secure access controls" if compliant

generate_message := "FAIL: Remote access is not consistently protected by MFA in GCP" if not compliant