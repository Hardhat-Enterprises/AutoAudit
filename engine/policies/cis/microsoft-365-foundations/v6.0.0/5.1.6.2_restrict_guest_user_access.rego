# METADATA
# title: Ensure that guest user access is restricted
# description: Restrict guest user access permissions in Entra ID.
# related_resources:
# - ref: https://learn.microsoft.com/en-us/entra/identity/users/users-restrict-guest-permissions
#   description: Restrict guest access permissions
# custom:
#   control_id: CIS-5.1.6.2
#   framework: cis
#   benchmark: microsoft-365-foundations
#   version: v6.0.0
#   severity: medium
#   service: EntraID
#   requires_permissions:
#   - Policy.Read.All

package cis.microsoft_365_foundations.v6_0_0.control_5_1_6_2

import rego.v1

default result := {
  "compliant": false,
  "message": "Unable to determine guestUserRoleId",
  "details": {},
}

# Known guestUserRoleId values (Microsoft docs):
# - Same as members: a0b1b346-4d3e-4e8b-98f8-753987be4970 (NOT compliant)
# - Limited access (default): 10dae51f-b6af-4016-8d66-8c2a99b929b3 (compliant)
# - Most restrictive: 2af84b1e-32c8-42b7-82bc-daa82404023b (compliant)

same_as_member := "a0b1b346-4d3e-4e8b-98f8-753987be4970" if { true }
limited := "10dae51f-b6af-4016-8d66-8c2a99b929b3" if { true }
restricted := "2af84b1e-32c8-42b7-82bc-daa82404023b" if { true }

ok if { input.guest_user_role_id == limited }
ok if { input.guest_user_role_id == restricted }

compliant_value := true if { ok } else := false if { true }

msg := "Guest user access is restricted" if { ok } else := "Guest user access is NOT restricted (guests have member-like permissions)" if { input.guest_user_role_id == same_as_member } else := "Unable to determine guestUserRoleId" if { input.guest_user_role_id == null } else := sprintf("Guest user access is NOT restricted (guestUserRoleId=%v)", [input.guest_user_role_id]) if { true }

result := out if {
  role_id := input.guest_user_role_id

  out := {
    "compliant": compliant_value,
    "message": msg,
    "details": {
      "guest_user_role_id": role_id,
    },
  }
}

