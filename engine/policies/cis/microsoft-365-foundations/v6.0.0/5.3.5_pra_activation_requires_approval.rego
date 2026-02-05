# METADATA
# title: Ensure approval is required for Privileged Role Administrator activation
# description: Require approval for Privileged Role Admin activation.
# related_resources:
# - ref: https://learn.microsoft.com/en-us/entra/id-governance/privileged-identity-management/pim-role-activation
#   description: PIM role activation settings (conceptual)
# custom:
#   control_id: CIS-5.3.5
#   framework: cis
#   benchmark: microsoft-365-foundations
#   version: v6.0.0
#   severity: critical
#   service: EntraID
#   requires_permissions:
#   - RoleManagementPolicy.Read.Directory

package cis.microsoft_365_foundations.v6_0_0.control_5_3_5

import rego.v1

default result := {
  "compliant": false,
  "message": "Unable to determine Privileged Role Administrator approval requirements",
  "details": {},
}

default compliant := false

compliant if { input.privileged_role_admin_approval_required == true }

msg := "Approval is required for Privileged Role Administrator activation" if { compliant }
msg := "Approval is NOT required for Privileged Role Administrator activation" if { input.privileged_role_admin_approval_required == false }
msg := "Unable to determine Privileged Role Administrator approval requirements" if { input.privileged_role_admin_approval_required == null }

result := output if {
  required := input.privileged_role_admin_approval_required

  output := {
    "compliant": compliant,
    "message": msg,
    "details": {
      "privileged_role_admin_policy": input.privileged_role_admin_policy,
      "approval_required": required,
    },
  }
}

