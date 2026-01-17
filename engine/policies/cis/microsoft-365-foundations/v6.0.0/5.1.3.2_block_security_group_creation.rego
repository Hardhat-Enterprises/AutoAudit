# METADATA
# title: Ensure users cannot create security groups
# description: Prevent users from creating security groups.
# related_resources:
# - ref: https://www.cisecurity.org/benchmark/microsoft_365
#   description: CIS Microsoft 365 Foundations Benchmark
# custom:
#   control_id: CIS-5.1.3.2
#   framework: cis
#   benchmark: microsoft-365-foundations
#   version: v6.0.0
#   severity: medium
#   service: EntraID
#   requires_permissions:
#   - Policy.Read.All

package cis.microsoft_365_foundations.v6_0_0.control_5_1_3_2

import rego.v1

default result := {
  "compliant": false,
  "message": "Unable to determine allowedToCreateSecurityGroups",
  "details": {},
}

compliant_value := true if { input.allowed_to_create_security_groups == false } else := false if { true }

msg := "Users cannot create security groups (allowedToCreateSecurityGroups=false)" if { input.allowed_to_create_security_groups == false } else := "Users can create security groups (allowedToCreateSecurityGroups=true)" if { input.allowed_to_create_security_groups == true } else := "Unable to determine allowedToCreateSecurityGroups" if { true }

result := out if {
  value := input.allowed_to_create_security_groups

  out := {
    "compliant": compliant_value,
    "message": msg,
    "details": {
      "allowed_to_create_security_groups": value,
    },
  }
}

