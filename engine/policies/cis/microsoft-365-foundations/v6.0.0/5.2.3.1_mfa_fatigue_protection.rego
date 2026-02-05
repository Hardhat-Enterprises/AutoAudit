# METADATA
# title: Ensure Microsoft Authenticator is configured to protect against MFA fatigue
# description: Configure Authenticator to prevent MFA fatigue attacks.
# related_resources:
# - ref: https://learn.microsoft.com/en-us/entra/identity/authentication/howto-mfa-number-match
#   description: Number matching (conceptual)
# custom:
#   control_id: CIS-5.2.3.1
#   framework: cis
#   benchmark: microsoft-365-foundations
#   version: v6.0.0
#   severity: high
#   service: EntraID
#   requires_permissions:
#   - Policy.Read.All

package cis.microsoft_365_foundations.v6_0_0.control_5_2_3_1

import rego.v1

default result := {
  "compliant": false,
  "message": "Unable to determine Microsoft Authenticator MFA fatigue protection settings",
  "details": {},
}

compliant_value := true if { input.number_matching_enabled == true } else := false if { true }

msg := "MFA fatigue protection is enabled (number matching required)" if { input.number_matching_enabled == true } else := "MFA fatigue protection is not enabled (number matching not required)" if { input.number_matching_enabled != true } else := "Unable to determine Microsoft Authenticator MFA fatigue protection settings" if { true }

result := output if {
  number_matching := input.number_matching_enabled
  app_ctx := input.display_app_information_enabled
  loc_ctx := input.display_location_information_enabled

  output := {
    "compliant": compliant_value,
    "message": msg,
    "details": {
      "state": input.state,
      "number_matching_enabled": number_matching,
      "display_app_information_enabled": app_ctx,
      "display_location_information_enabled": loc_ctx,
      "include_targets_count": count(input.include_targets),
      "exclude_targets_count": count(input.exclude_targets),
    },
  }
}

