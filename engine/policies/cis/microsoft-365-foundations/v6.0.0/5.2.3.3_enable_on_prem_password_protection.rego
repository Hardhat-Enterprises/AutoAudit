# METADATA
# title: Ensure password protection is enabled for on-prem Active Directory
# description: Enable password protection for on-premises AD.
# related_resources:
# - ref: https://learn.microsoft.com/en-us/entra/identity/authentication/concept-password-ban-bad
#   description: Password protection and banned passwords (conceptual)
# custom:
#   control_id: CIS-5.2.3.3
#   framework: cis
#   benchmark: microsoft-365-foundations
#   version: v6.0.0
#   severity: medium
#   service: EntraID
#   requires_permissions:
#   - Directory.Read.All

package cis.microsoft_365_foundations.v6_0_0.control_5_2_3_3

import rego.v1

default result := {
  "compliant": false,
  "message": "Unable to determine on-prem password protection configuration",
  "details": {},
}

default compliant := false

compliant if {
  input.on_prem_protection_enabled == true
}

msg := "On-prem password protection is enabled" if { compliant }
msg := "On-prem password protection is not enabled" if { not compliant }

result := output if {
  enabled := input.on_prem_protection_enabled

  output := {
    "compliant": compliant,
    "message": msg,
    "details": {
      "on_prem_protection_enabled": enabled,
      "enforce_custom_banned_passwords": input.enforce_custom_banned_passwords,
    },
  }
}

