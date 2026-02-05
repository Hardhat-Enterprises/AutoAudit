# METADATA
# title: Ensure that between two and four global admins are designated
# description: |
#   Maintain between 2-4 global administrators to ensure operational continuity
#   while minimizing attack surface. Having fewer than 2 creates a single point
#   of failure, while having more than 4 unnecessarily expands the attack surface
#   and increases the risk of credential compromise.
# related_resources:
# - ref: https://www.cisecurity.org/benchmark/microsoft_365
#   description: CIS Microsoft 365 Foundations Benchmark
# custom:
#   control_id: CIS-1.1.3
#   framework: cis
#   benchmark: microsoft-365-foundations
#   version: v6.0.0
#   severity: high
#   service: EntraID
#   requires_permissions:
#   - RoleManagement.Read.Directory
#   - User.Read.All

package cis.microsoft_365_foundations.v6_0_0.control_1_1_3

import rego.v1

default result := {
  "compliant": false,
  "message": "Evaluation failed: unable to retrieve Global Administrator role membership",
  "details": {}
}

default compliant := false

compliant if {
  admin_count := input.global_admin_count
  admin_count >= 2
  admin_count <= 4
}

result := output if {
  admin_count := input.global_admin_count
  admins := get_array(input, "global_admins")

  output := {
    "compliant": compliant,
    "message": generate_message(admin_count),
    "affected_resources": admins,
    "details": {
      "global_admin_count": admin_count,
      "recommended_min": 2,
      "recommended_max": 4
    }
  }
}

generate_message(admin_count) := msg if {
  admin_count < 2
  msg := sprintf("Only %d global admin(s) found. Minimum 2 recommended for continuity.", [admin_count])
}

generate_message(admin_count) := msg if {
  admin_count > 4
  msg := sprintf("%d global admins found. Maximum 4 recommended to minimize attack surface.", [admin_count])
}

generate_message(admin_count) := msg if {
  admin_count >= 2
  admin_count <= 4
  msg := sprintf("%d global admins configured (within recommended range of 2-4)", [admin_count])
}

get_array(obj, key) := value if {
  value := obj[key]
} else := []
