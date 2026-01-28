# METADATA
# title: Ensure custom banned passwords lists are used
# description: Configure custom banned password list.
# related_resources:
# - ref: https://learn.microsoft.com/en-us/entra/identity/authentication/concept-password-ban-bad
#   description: Password protection and banned passwords (conceptual)
# custom:
#   control_id: CIS-5.2.3.2
#   framework: cis
#   benchmark: microsoft-365-foundations
#   version: v6.0.0
#   severity: medium
#   service: EntraID
#   requires_permissions:
#   - Directory.Read.All

package cis.microsoft_365_foundations.v6_0_0.control_5_2_3_2

import rego.v1

default result := {
  "compliant": false,
  "message": "Unable to determine custom banned password list configuration",
  "details": {},
}

compliant_value := true if { input.banned_password_list_enabled == true } else := false if { true }

msg := "Custom banned password list is enabled" if { input.banned_password_list_enabled == true } else := "Custom banned password list is not enabled" if { input.banned_password_list_enabled != true } else := "Unable to determine custom banned password list configuration" if { true }

banned_list_present := true if { input.banned_password_list != null; input.banned_password_list != "" } else := false if { true }

result := output if {
  enabled := input.banned_password_list_enabled
  list := input.banned_password_list

  output := {
    "compliant": compliant_value,
    "message": msg,
    "details": {
      "banned_password_list_enabled": enabled,
      "banned_password_list_present": banned_list_present,
    },
  }
}

