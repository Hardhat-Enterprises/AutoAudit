# METADATA
# title: Ensure user consent to apps accessing company data on their behalf is not allowed
# description: Block user consent to applications for company data.
# related_resources:
# - ref: https://learn.microsoft.com/en-us/entra/identity/enterprise-apps/configure-user-consent
#   description: Configure user consent settings in Entra ID
# custom:
#   control_id: CIS-5.1.5.1
#   framework: cis
#   benchmark: microsoft-365-foundations
#   version: v6.0.0
#   severity: high
#   service: EntraID
#   requires_permissions:
#   - Policy.Read.All

package cis.microsoft_365_foundations.v6_0_0.control_5_1_5_1

import rego.v1

default result := {
  "compliant": false,
  "message": "Unable to determine user consent settings (permissionGrantPoliciesAssigned)",
  "details": {},
}

compliant if {
  perms := input.default_user_role_permissions
  assigned := perms.permissionGrantPoliciesAssigned
  assigned == []
}

compliant_value := true if { compliant } else := false if { true }

assigned_count := count(assigned) if {
  perms := input.default_user_role_permissions
  assigned := perms.permissionGrantPoliciesAssigned
  assigned != null
} else := null if { true }

msg := "User consent to apps is disabled (permissionGrantPoliciesAssigned is empty)" if {
  compliant
} else := sprintf(
  "User consent to apps is enabled/restricted (permissionGrantPoliciesAssigned has %d entries)",
  [assigned_count],
) if {
  perms := input.default_user_role_permissions
  assigned := perms.permissionGrantPoliciesAssigned
  assigned != null
  not compliant
} else := "Unable to determine user consent settings (permissionGrantPoliciesAssigned missing)" if { true }

# According to Graph, user consent is controlled by authorizationPolicy.defaultUserRolePermissions.permissionGrantPoliciesAssigned.
# CIS intent: user consent should be disabled (empty list).
result := out if {
  perms := input.default_user_role_permissions
  assigned := perms.permissionGrantPoliciesAssigned

  is_empty := assigned == []  # strict: disabled
  ok := is_empty

  out := {
    "compliant": compliant_value,
    "message": msg,
    "details": {
      "permission_grant_policies_assigned": assigned,
      "permission_grant_policies_assigned_count": assigned_count,
    },
  }
}

