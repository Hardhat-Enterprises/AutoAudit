# METADATA
# title: Ensure that only organizationally managed/approved public groups exist
# description: Public groups should be reviewed and managed by the organization.
# related_resources:
# - ref: https://www.cisecurity.org/benchmark/microsoft_365
#   description: CIS Microsoft 365 Foundations Benchmark
# custom:
#   control_id: CIS-1.2.1
#   framework: cis
#   benchmark: microsoft-365-foundations
#   version: v6.0.0
#   severity: medium
#   service: EntraID
#   requires_permissions:
#   - Group.Read.All

package cis.microsoft_365_foundations.v6_0_0.control_1_2_1

import rego.v1

default result := {
  "compliant": false,
  "message": "Unable to determine public group configuration",
  "details": {},
}

publics := object.get(input, "public_groups", []) if { true }

compliant_value := true if { count(publics) == 0 } else := false if { true }

msg := "No public groups exist" if { compliant_value } else := sprintf("%d public group(s) exist and require organizational approval", [count(publics)]) if { true }

# This is a best-effort automated check.
# We treat any Public groups as requiring review and fail the control so it remains actionable.
result := output if {
  output := {
    "compliant": compliant_value,
    "message": msg,
    "details": {
      "total_groups": input.total_groups,
      "public_groups_count": count(publics),
      "public_groups": [{"id": g.id, "displayName": g.displayName} | some g in publics],
    },
  }
}

