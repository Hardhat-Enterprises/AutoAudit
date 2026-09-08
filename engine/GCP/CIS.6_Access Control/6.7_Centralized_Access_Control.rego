# METADATA
# title: Ensure access control is centralized (GCP)
# description: |
#   Access to GCP resources must be centrally managed via Google Workspace or Cloud Identity
#   as the identity provider, with IAM used for authorization. Applications should be integrated
#   via SSO or Identity-Aware Proxy (IAP), and access changes must propagate consistently across
#   all connected systems. Evidence of change propagation should be verifiable via logs.
# related_resources:
# - ref: https://cloud.google.com/iam/docs
#   description: GCP IAM Documentation
# - ref: https://cloud.google.com/iap/docs
#   description: Identity-Aware Proxy Documentation
# custom:
#   control_id: CIS-6.7
#   framework: cis
#   benchmark: gcp-foundations
#   version: v2.0.0
#   severity: high
#   service: IAM
#   requires_permissions:
#   - iam.securityReviewer
#   - logging.viewer

package cis.gcp_foundations.v2_0_0.control_6_7

import rego.v1

default compliant := false

# ---------------------------
# Compliance Logic
# ---------------------------
compliant if {
  input.central_directory_used == true      # Google Workspace / Cloud Identity
  input.sso_enabled == true                # SSO or IAP enforced
  input.app_integration_count > 0          # Apps integrated with IdP
  has_change_propagation_example
}

# Validate at least one example of centralized change propagation
has_change_propagation_example if {
  some e in input.change_events

  e.directory_change == true        # Change made in central identity system
  e.downstream_effect == true       # Reflected in IAM / apps
}

# ---------------------------
# Result Output
# ---------------------------
result := {
  "compliant": compliant,
  "message": generate_message,
  "details": {
    "integrated_apps": input.app_integration_count
  }
}

# ---------------------------
# Message Logic
# ---------------------------
generate_message := "PASS: Access control is centralized via GCP identity services and consistently enforced across systems" if compliant

generate_message := "FAIL: Access control is not centrally managed in GCP or lacks propagation evidence" if not compliant