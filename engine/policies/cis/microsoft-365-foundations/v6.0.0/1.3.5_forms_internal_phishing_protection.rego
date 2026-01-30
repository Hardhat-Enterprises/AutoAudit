# METADATA
# title: Ensure internal phishing protection for Forms is enabled
# description: |
#   Internal phishing protection helps prevent misuse of Microsoft Forms for
#   phishing within the organization. Enable internal phishing protection to
#   reduce the risk of credential harvesting and social engineering attacks.
# related_resources:
# - ref: https://www.cisecurity.org/benchmark/microsoft_365
#   description: CIS Microsoft 365 Foundations Benchmark
# custom:
#   control_id: CIS-1.3.5
#   framework: cis
#   benchmark: microsoft-365-foundations
#   version: v6.0.0
#   severity: medium
#   service: Forms
#   requires_permissions:
#   - OrgSettings-Forms.Read.All

package cis.microsoft_365_foundations.v6_0_0.control_1_3_5

import rego.v1

default result := {
  "compliant": false,
  "message": "Evaluation failed: unable to retrieve Microsoft Forms settings",
  "details": {}
}

result := output if {
  enabled := input.internal_phishing_protection_enabled

  output := {
    "compliant": enabled == true,
    "message": generate_message(enabled),
    "affected_resources": generate_affected(enabled),
    "details": {
      "internal_phishing_protection_enabled": enabled,
      "external_sharing_enabled": input.external_sharing_enabled,
      "external_send_form_enabled": input.external_send_form_enabled,
      "external_share_collaborating_enabled": input.external_share_collaborating_enabled,
      "external_share_template_enabled": input.external_share_template_enabled,
      "external_share_result_enabled": input.external_share_result_enabled,
      "bing_search_enabled": input.bing_search_enabled,
      "record_identity_by_default_enabled": input.record_identity_by_default_enabled,
      "collector_error": input.collector_error
    }
  }
}

generate_message(true) := "Microsoft Forms internal phishing protection is enabled"
generate_message(false) := "Microsoft Forms internal phishing protection is not enabled"
generate_message(null) := "Unable to determine Microsoft Forms internal phishing protection setting"

generate_affected(true) := []
generate_affected(false) := ["Microsoft Forms internal phishing protection is disabled"]
generate_affected(null) := ["Microsoft Forms internal phishing protection setting unknown"]
