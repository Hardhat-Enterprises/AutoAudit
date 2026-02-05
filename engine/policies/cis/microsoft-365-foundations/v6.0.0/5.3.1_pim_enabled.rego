# METADATA
# title: Ensure 'Privileged Identity Management' is used to manage roles
# description: Use PIM for privileged role management.
# related_resources:
# - ref: https://learn.microsoft.com/en-us/entra/id-governance/privileged-identity-management/pim-configure
#   description: Privileged Identity Management (conceptual)
# custom:
#   control_id: CIS-5.3.1
#   framework: cis
#   benchmark: microsoft-365-foundations
#   version: v6.0.0
#   severity: high
#   service: EntraID
#   requires_permissions:
#   - RoleManagementPolicy.Read.Directory

package cis.microsoft_365_foundations.v6_0_0.control_5_3_1

import rego.v1

default result := {
  "compliant": false,
  "message": "Unable to determine if PIM is enabled",
  "details": {},
}

default compliant := false

compliant if { input.pim_enabled == true }

msg := "PIM is enabled (role management policies present)" if { compliant }
msg := "PIM does not appear to be enabled (no role management policies found)" if { not compliant }

result := output if {
  enabled := input.pim_enabled

  output := {
    "compliant": compliant,
    "message": msg,
    "details": {
      "total_policies": input.total_policies,
    },
  }
}

