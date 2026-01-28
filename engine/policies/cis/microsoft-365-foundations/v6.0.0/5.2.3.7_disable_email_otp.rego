# METADATA
# title: Ensure the email OTP authentication method is disabled
# description: Disable email OTP authentication.
# related_resources:
# - ref: https://learn.microsoft.com/en-us/graph/api/resources/authenticationmethodspolicy
#   description: Authentication methods policy
# custom:
#   control_id: CIS-5.2.3.7
#   framework: cis
#   benchmark: microsoft-365-foundations
#   version: v6.0.0
#   severity: medium
#   service: EntraID
#   requires_permissions:
#   - Policy.Read.All

package cis.microsoft_365_foundations.v6_0_0.control_5_2_3_7

import rego.v1

default result := {
  "compliant": false,
  "message": "Unable to determine Email OTP authentication method status",
  "details": {},
}

default compliant := false

compliant if { input.email_otp_enabled == false }

msg := "Email OTP authentication method is disabled" if { compliant }
msg := "Email OTP authentication method is enabled" if { input.email_otp_enabled == true }
msg := "Unable to determine Email OTP authentication method status" if { input.email_otp_enabled == null }

result := output if {
  email := input.email_otp_enabled

  output := {
    "compliant": compliant,
    "message": msg,
    "details": {
      "email_otp_enabled": email,
    },
  }
}

