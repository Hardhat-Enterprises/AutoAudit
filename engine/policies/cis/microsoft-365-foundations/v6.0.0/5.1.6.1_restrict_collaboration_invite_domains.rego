# METADATA
# title: Ensure that collaboration invitations are sent to allowed domains only
# description: Restrict external collaboration to allowed domains/tenants.
# related_resources:
# - ref: https://learn.microsoft.com/en-us/graph/api/crosstenantaccesspolicy-overview
#   description: Cross-tenant access settings
# custom:
#   control_id: CIS-5.1.6.1
#   framework: cis
#   benchmark: microsoft-365-foundations
#   version: v6.0.0
#   severity: medium
#   service: EntraID
#   requires_permissions:
#   - Policy.Read.All

package cis.microsoft_365_foundations.v6_0_0.control_5_1_6_1

import rego.v1

default result := {
  "compliant": false,
  "message": "Unable to determine cross-tenant access restrictions",
  "details": {},
}

partners := object.get(input, "partners", []) if { true }
partners_count := object.get(input, "partners_count", 0) if { true }

default_inbound_access_type := access_type if {
  inbound := object.get(input, "b2b_collaboration_inbound", {})
  users_and_groups := object.get(inbound, "usersAndGroups", {})
  access_type := object.get(users_and_groups, "accessType", "")
}

compliant_value := true if {
  partners_count > 0
  default_inbound_access_type == "blocked"
} else := false if { true }

msg := sprintf("Cross-tenant collaboration is restricted by default (partners=%d, accessType=%v)", [partners_count, default_inbound_access_type]) if { compliant_value } else := sprintf("Cross-tenant collaboration is not sufficiently restricted (partners=%d, accessType=%v)", [partners_count, default_inbound_access_type]) if { true }

# Heuristic evaluation:
# - Consider compliant when the tenant has explicit partner configuration (partners_count > 0)
#   and the default inbound B2B collaboration access is not wide-open.
result := output if {
  output := {
    "compliant": compliant_value,
    "message": msg,
    "details": {
      "partners_count": partners_count,
      "partner_tenant_ids": [p.tenantId | some p in partners; p.tenantId != null],
      "default_inbound_access_type": default_inbound_access_type,
    },
  }
}

