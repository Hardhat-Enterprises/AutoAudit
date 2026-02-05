# METADATA
# title: Ensure 'Restrict non-admin users from creating tenants' is set to 'Yes'
# description: Prevent non-admin users from creating tenants.
# related_resources:
# - ref: https://www.cisecurity.org/benchmark/microsoft_365
#   description: CIS Microsoft 365 Foundations Benchmark
# custom:
#   control_id: CIS-5.1.2.3
#   framework: cis
#   benchmark: microsoft-365-foundations
#   version: v6.0.0
#   severity: medium
#   service: EntraID
#   requires_permissions:
#   - Policy.Read.All

package cis.microsoft_365_foundations.v6_0_0.control_5_1_2_3

import rego.v1

default result := {
  "compliant": false,
  "message": "Unable to determine allowedToCreateTenants",
  "details": {},
}

compliant_value := true if { input.allowed_to_create_tenants == false } else := false if { true }

msg := "Non-admin users cannot create tenants (allowedToCreateTenants=false)" if { input.allowed_to_create_tenants == false } else := "Non-admin users can create tenants (allowedToCreateTenants=true)" if { input.allowed_to_create_tenants == true } else := "Unable to determine allowedToCreateTenants" if { true }

result := out if {
  value := input.allowed_to_create_tenants

  out := {
    "compliant": compliant_value,
    "message": msg,
    "details": {
      "allowed_to_create_tenants": value,
    },
  }
}

