# METADATA
# title: Ensure a dynamic group for guest users is created
# description: Create a dynamic group to manage guest users.
# related_resources:
# - ref: https://learn.microsoft.com/en-us/entra/identity/users/groups-dynamic-membership
#   description: Dynamic membership rules (conceptual)
# custom:
#   control_id: CIS-5.1.3.1
#   framework: cis
#   benchmark: microsoft-365-foundations
#   version: v6.0.0
#   severity: medium
#   service: EntraID
#   requires_permissions:
#   - Group.Read.All

package cis.microsoft_365_foundations.v6_0_0.control_5_1_3_1

import rego.v1

default result := {
  "compliant": false,
  "message": "No dynamic guest user group detected",
  "details": {},
}

# Look for dynamic membership rules referencing Guest user type.
is_guest_rule(rule) if {
  lower(rule) != ""
  contains(lower(rule), "guest")
}

compliant_value := true if {
  dyn := input.dynamic_groups
  matching := [g |
    some g in dyn
    rule := g.membershipRule
    rule != null
    is_guest_rule(rule)
  ]
  count(matching) > 0
} else := false if { true }

msg := sprintf("Found %d dynamic group(s) targeting guest users", [count(matching)]) if {
  dyn := input.dynamic_groups
  matching := [g |
    some g in dyn
    rule := g.membershipRule
    rule != null
    is_guest_rule(rule)
  ]
  count(matching) > 0
} else := "No dynamic guest user group detected" if { true }

result := output if {
  dyn := input.dynamic_groups
  matching := [g |
    some g in dyn
    rule := g.membershipRule
    rule != null
    is_guest_rule(rule)
  ]

  output := {
    "compliant": compliant_value,
    "message": msg,
    "details": {
      "dynamic_groups_count": input.dynamic_groups_count,
      "matching_groups": [{"id": g.id, "displayName": g.displayName, "membershipRule": g.membershipRule} | some g in matching],
    },
  }
}

