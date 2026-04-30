# METADATA
# title: Ensure the GA role is not added as a local administrator during Entra join
# description: |
#   When a device joins Entra ID, automatically granting the Global Administrator
#   role local admin rights on that machine creates unnecessary privilege exposure.
#   The GA role should not be part of the local administrators configuration for
#   joined devices.
# related_resources:
# - ref: https://www.cisecurity.org/benchmark/microsoft_365
#   description: CIS Microsoft 365 Foundations Benchmark
# custom:
#   control_id: CIS-5.1.4.3
#   framework: cis
#   benchmark: microsoft-365-foundations
#   version: v6.0.0
#   severity: medium
#   service: EntraID
#   requires_permissions:
#   - Policy.Read.DeviceConfiguration

package cis.microsoft_365_foundations.v6_0_0.control_5_1_4_3

import rego.v1

default result := {
    "compliant": false,
    "message": "Evaluation failed: unable to retrieve device registration policy",
    "details": {},
}

compliant := true if {
    input.global_admins_enabled_on_join == false
} else := false

result := output if {
    ga_enabled := input.global_admins_enabled_on_join
    output := {
        "compliant": compliant,
        "message": build_message(ga_enabled),
        "affected_resources": [],
        "details": {
            "global_admins_enabled_on_join": ga_enabled,
            "local_admins_config": object.get(input, "local_admins_config", null),
        },
    }
}

build_message(false) := "Global Administrator role is not assigned local admin rights on Entra-joined devices"
build_message(null) := "Unable to determine whether GA role is granted local admin rights on join; azureADJoin.localAdministratorsConfiguration not returned by API"
build_message(true) := "Global Administrator role is configured as a local administrator on Entra-joined devices"
