# METADATA
# title: Ensure 'User owned apps and services' is restricted
# description: |
#   Allowing users to own apps and services increases the risk of unauthorized
#   application integrations and data exposure. Restrict this capability so that
#   only approved administrators can enable and manage user apps and services.
# related_resources:
# - ref: https://www.cisecurity.org/benchmark/microsoft_365
#   description: CIS Microsoft 365 Foundations Benchmark
# custom:
#   control_id: CIS-1.3.4
#   framework: cis
#   benchmark: microsoft-365-foundations
#   version: v6.0.0
#   severity: medium
#   service: EntraID
#   requires_permissions:
#   - Policy.Read.All

package cis.microsoft_365_foundations.v6_0_0.control_1_3_4

import rego.v1

default result := {
  "compliant": false,
  "message": "Evaluation failed: unable to retrieve Microsoft 365 Apps and Services settings",
  "details": {}
}

result := output if {
  enabled := input.user_owned_apps_enabled

  output := {
    # CIS intent: restricted => disabled
    "compliant": enabled == false,
    "message": generate_message(enabled),
    "affected_resources": generate_affected(enabled),
    "details": {
      "user_owned_apps_enabled": enabled,
      "is_office_store_enabled": input.is_office_store_enabled
    }
  }
}

generate_message(true) := "User owned apps and services are not restricted (enabled)"
generate_message(false) := "User owned apps and services are restricted (disabled)"
generate_message(null) := "Unable to determine whether user owned apps and services are restricted"

generate_affected(false) := []
generate_affected(true) := ["User owned apps and services are enabled"]
generate_affected(null) := ["User owned apps and services setting unknown"]
