# METADATA
# title: Ensure the ability to join devices to Entra is restricted
# description: Restrict device join to authorized users.
# related_resources:
# - ref: https://learn.microsoft.com/en-us/entra/identity/devices/device-join
#   description: Device join settings (conceptual)
# custom:
#   control_id: CIS-5.1.4.1
#   framework: cis
#   benchmark: microsoft-365-foundations
#   version: v6.0.0
#   severity: medium
#   service: EntraID
#   requires_permissions:
#   - Policy.Read.DeviceConfiguration

package cis.microsoft_365_foundations.v6_0_0.control_5_1_4_1

import rego.v1

default result := {
  "compliant": false,
  "message": "Unable to determine device join restrictions",
  "details": {},
}

compliant if {
  input.azure_ad_join_allowed_users != null
  input.azure_ad_join_allowed_users != "all"
}

compliant_value := true if { compliant } else := false if { true }

msg := "Device join is restricted to selected users/groups" if { compliant } else := "Device join appears to be allowed broadly (allowedUsers=all or missing)" if { true }

result := output if {
  users := input.azure_ad_join_allowed_users
  groups := input.azure_ad_join_allowed_groups

  # Compliant when join is not broadly allowed to everyone.
  # We treat "all" / empty / null as non-compliant.
  output := {
    "compliant": compliant_value,
    "message": msg,
    "details": {
      "allowed_users": users,
      "allowed_groups": groups,
      "user_device_quota": input.user_device_quota,
    },
  }
}

