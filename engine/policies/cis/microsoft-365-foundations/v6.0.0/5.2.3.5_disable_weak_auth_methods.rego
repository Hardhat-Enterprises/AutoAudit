# METADATA
# title: Ensure weak authentication methods are disabled
# description: Disable SMS and voice authentication methods.
# related_resources:
# - ref: https://learn.microsoft.com/en-us/graph/api/resources/authenticationmethodspolicy
#   description: Authentication methods policy
# custom:
#   control_id: CIS-5.2.3.5
#   framework: cis
#   benchmark: microsoft-365-foundations
#   version: v6.0.0
#   severity: medium
#   service: EntraID
#   requires_permissions:
#   - Policy.Read.All

package cis.microsoft_365_foundations.v6_0_0.control_5_2_3_5

import rego.v1

default result := {
  "compliant": false,
  "message": "Unable to determine SMS/Voice authentication method status",
  "details": {},
}

default compliant := false

compliant if {
  input.sms_enabled == false
  input.voice_enabled == false
}

msg := "Weak authentication methods (SMS, Voice) are disabled" if { compliant }
msg := sprintf("Weak authentication methods enabled (sms=%v, voice=%v)", [input.sms_enabled, input.voice_enabled]) if { not compliant }

result := output if {
  sms := input.sms_enabled
  voice := input.voice_enabled

  output := {
    "compliant": compliant,
    "message": msg,
    "details": {
      "sms_enabled": sms,
      "voice_enabled": voice,
    },
  }
}

