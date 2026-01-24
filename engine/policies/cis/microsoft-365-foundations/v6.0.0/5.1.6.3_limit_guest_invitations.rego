# METADATA
# title: Ensure guest user invitations are limited to the Guest Inviter role
# description: Limit who can invite guest users into the tenant.
# related_resources:
# - ref: https://learn.microsoft.com/en-us/graph/api/authorizationpolicy-get
#   description: authorizationPolicy resource type
# custom:
#   control_id: CIS-5.1.6.3
#   framework: cis
#   benchmark: microsoft-365-foundations
#   version: v6.0.0
#   severity: medium
#   service: EntraID
#   requires_permissions:
#   - Policy.Read.All

package cis.microsoft_365_foundations.v6_0_0.control_5_1_6_3

import rego.v1

default result := {
  "compliant": false,
  "message": "Unable to determine allowInvitesFrom",
  "details": {},
}

compliant_value := true if { input.allow_invites_from == "adminsAndGuestInviters" } else := false if { true }

msg := "Guest invitations are limited to admins and Guest Inviter role (allowInvitesFrom=adminsAndGuestInviters)" if { input.allow_invites_from == "adminsAndGuestInviters" } else := sprintf("Guest invitations are not sufficiently restricted (allowInvitesFrom=%v)", [input.allow_invites_from]) if { input.allow_invites_from != null; input.allow_invites_from != "adminsAndGuestInviters" } else := "Unable to determine allowInvitesFrom" if { input.allow_invites_from == null } else := "Unable to determine allowInvitesFrom" if { true }

result := out if {
  v := input.allow_invites_from

  # Expected: only admins and Guest Inviter role can invite

  out := {
    "compliant": compliant_value,
    "message": msg,
    "details": {
      "allow_invites_from": v,
    },
  }
}

