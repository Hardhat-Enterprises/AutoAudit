# METADATA
# title: Ensure approval is required for Global Administrator role activation
# description: Require approval for Global Admin role activation.
# related_resources:
# - ref: https://learn.microsoft.com/en-us/entra/id-governance/privileged-identity-management/pim-role-activation
#   description: PIM role activation settings (conceptual)
# custom:
#   control_id: CIS-5.3.4
#   framework: cis
#   benchmark: microsoft-365-foundations
#   version: v6.0.0
#   severity: critical
#   service: EntraID
#   requires_permissions:
#   - RoleManagementPolicy.Read.Directory

package cis.microsoft_365_foundations.v6_0_0.control_5_3_4

import rego.v1

default result := {
  "compliant": false,
  "message": "Unable to determine Global Administrator approval requirements",
  "details": {},
}

default compliant := false

compliant if { input.global_admin_approval_required == true }

msg := "Approval is required for Global Administrator activation" if { compliant }
msg := "Approval is NOT required for Global Administrator activation" if { input.global_admin_approval_required == false }
msg := "Unable to determine Global Administrator approval requirements" if { input.global_admin_approval_required == null }

result := output if {
  required := input.global_admin_approval_required

  output := {
    "compliant": compliant,
    "message": msg,
    "details": {
      "global_admin_policy": input.global_admin_policy,
      "approval_required": required,
      "mfa_required": input.global_admin_mfa_required,
      "justification_required": input.global_admin_justification_required,
      "max_activation_duration": input.global_admin_max_activation_duration,
    },
  }
}

