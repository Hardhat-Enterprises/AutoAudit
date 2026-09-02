# METADATA
# title: Ensure the GA role is not added as a local administrator during Entra join
# description: Prevent Global Administrators from automatically receiving local administrator access on Entra-joined devices.
# related_resources:
# - ref: https://learn.microsoft.com/en-us/entra/identity/devices/assign-local-admin
#   description: Microsoft Entra joined device local administrator management
# custom:
#   control_id: CIS-5.1.4.3
#   framework: cis
#   benchmark: microsoft-365-foundations
#   version: v6.0.0
#   severity: medium
#   service: EntraID
#   requires_permissions:
#   - Policy.Read.DeviceConfiguration

package cis.microsoft_365_foundations.v6_0_0.control_5_1_4_3

import rego.v1

default result := {
  "compliant": false,
  "message": "Unable to determine whether Global Administrators are added as local administrators",
  "details": {},
}

compliant_value := true if {
  input.global_admins_as_local_admin == false
} else := false if {
  true
}

msg := "Global Administrators are not automatically added as local administrators" if {
  input.global_admins_as_local_admin == false
} else := "Global Administrators are automatically added as local administrators" if {
  input.global_admins_as_local_admin == true
} else := "Unable to determine whether Global Administrators are added as local administrators" if {
  true
}

result := output if {
  value := input.global_admins_as_local_admin

  output := {
    "compliant": compliant_value,
    "message": msg,
    "details": {
      "enable_global_admins": value,
    },
  }
}