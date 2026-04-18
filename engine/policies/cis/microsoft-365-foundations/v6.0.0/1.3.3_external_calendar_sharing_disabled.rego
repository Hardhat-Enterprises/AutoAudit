# METADATA
# title: Ensure 'External sharing' of calendars is not available
# description: |
#   Prevent users from sharing calendar information with external 
#   users to reduce information leakage and maintain privacy.
# related_resources:
# - ref: https://learn.microsoft.com/en-us/exchange/sharing/organization-relationships/create-an-organization-relationship
#   description: Exchange sharing policies
# custom:
#   control_id: CIS-1.3.3
#   framework: cis
#   benchmark: microsoft-365-foundations
#   version: v6.0.0
#   severity: medium
#   service: Exchange
#   requires_permissions:
#   - Exchange.Manage

package cis.microsoft_365_foundations.v6_0_0.control_1_3_3

import rego.v1

default result := {
  "compliant": false,
  "message": "Unable to retrieve sharing policy configuration",
  "details": {},
}

default compliant := false

# Compliant when no policies allow external sharing
compliant if {
  count(input.policies_allowing_external) == 0
}

msg := "External calendar sharing is properly disabled" if {
  compliant
}

msg := sprintf("%d policy(s) allow external calendar sharing", [count(input.policies_allowing_external)]) if {
  not compliant
}

result := output if {
  external_policies := input.policies_allowing_external
  
  output := {
    "compliant": compliant,
    "message": msg,
    "affected_resources": [p.name | some p in external_policies],
    "details": {
      "total_policies": input.total_policies,
      "policies_allowing_external_count": count(external_policies),
      "policies_allowing_external": external_policies,
    },
  }
}