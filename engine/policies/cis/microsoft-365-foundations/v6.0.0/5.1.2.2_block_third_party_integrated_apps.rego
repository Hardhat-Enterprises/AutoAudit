# METADATA
# title: Ensure third party integrated applications are not allowed
# description: Block third-party application registration.
# related_resources:
# - ref: https://www.cisecurity.org/benchmark/microsoft_365
#   description: CIS Microsoft 365 Foundations Benchmark
# custom:
#   control_id: CIS-5.1.2.2
#   framework: cis
#   benchmark: microsoft-365-foundations
#   version: v6.0.0
#   severity: medium
#   service: EntraID
#   requires_permissions:
#   - Policy.Read.All

package cis.microsoft_365_foundations.v6_0_0.control_5_1_2_2

import rego.v1

default result := {
  "compliant": false,
  "message": "Unable to determine allowedToCreateApps",
  "details": {},
}

compliant_value := true if { input.allowed_to_create_apps == false } else := false if { true }

msg := "Third party integrated applications are not allowed (allowedToCreateApps=false)" if { input.allowed_to_create_apps == false } else := "Third party integrated applications are allowed (allowedToCreateApps=true)" if { input.allowed_to_create_apps == true } else := "Unable to determine allowedToCreateApps" if { true }

result := out if {
  value := input.allowed_to_create_apps

  out := {
    "compliant": compliant_value,
    "message": msg,
    "details": {
      "allowed_to_create_apps": value,
    },
  }
}

