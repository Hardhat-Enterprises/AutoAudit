# METADATA
# title: Ensure the admin consent workflow is enabled
# description: Enable admin consent workflow for apps.
# related_resources:
# - ref: https://learn.microsoft.com/en-us/entra/identity/enterprise-apps/configure-admin-consent-workflow
#   description: Configure the admin consent workflow
# custom:
#   control_id: CIS-5.1.5.2
#   framework: cis
#   benchmark: microsoft-365-foundations
#   version: v6.0.0
#   severity: medium
#   service: EntraID
#   requires_permissions:
#   - Policy.Read.All

package cis.microsoft_365_foundations.v6_0_0.control_5_1_5_2

import rego.v1

default result := {
  "compliant": false,
  "message": "Evaluation failed: unable to retrieve admin consent request policy",
  "details": {},
}

compliant_value := true if { input.is_enabled == true } else := false if { true }

msg := "Admin consent workflow is enabled" if { input.is_enabled == true } else := "Admin consent workflow is disabled" if { input.is_enabled == false } else := "Unable to determine admin consent workflow state" if { true }

result := output if {
  enabled := input.is_enabled
  reviewers := input.reviewers

  has_reviewers := count(reviewers) > 0

  output := {
    "compliant": compliant_value,
    "message": msg,
    "details": {
      "is_enabled": enabled,
      "reviewers_count": count(reviewers),
      "has_reviewers": has_reviewers,
      "notify_reviewers": input.notify_reviewers,
      "reminders_enabled": input.reminders_enabled,
      "request_duration_in_days": input.request_duration_in_days,
    },
  }
}

