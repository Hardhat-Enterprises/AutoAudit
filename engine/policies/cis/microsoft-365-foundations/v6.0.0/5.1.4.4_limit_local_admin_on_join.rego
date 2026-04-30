# METADATA
# title: Ensure local administrator assignment is limited during Entra join
# description: |
#   By default, the user registering a device may be granted local administrator
#   rights on that device. Restricting this prevents standard users from gaining
#   local admin access simply by joining a machine to Entra ID.
# related_resources:
# - ref: https://www.cisecurity.org/benchmark/microsoft_365
#   description: CIS Microsoft 365 Foundations Benchmark
# custom:
#   control_id: CIS-5.1.4.4
#   framework: cis
#   benchmark: microsoft-365-foundations
#   version: v6.0.0
#   severity: medium
#   service: EntraID
#   requires_permissions:
#   - Policy.Read.DeviceConfiguration

package cis.microsoft_365_foundations.v6_0_0.control_5_1_4_4

import rego.v1

default result := {
    "compliant": false,
    "message": "Evaluation failed: unable to retrieve device registration policy",
    "details": {},
}

compliant := true if {
    input.registering_users_local_admin != null
    lower(input.registering_users_local_admin) == "notallowed"
} else := false

result := output if {
    reg_users := input.registering_users_local_admin
    output := {
        "compliant": compliant,
        "message": build_message(reg_users),
        "affected_resources": [],
        "details": {
            "registering_users_local_admin": reg_users,
            "local_admins_config": object.get(input, "local_admins_config", null),
        },
    }
}

build_message(null) := "Unable to determine local admin assignment for registering users; azureADJoin.localAdministratorsConfiguration not returned by API"
build_message(val) := "Registering users are not granted local administrator rights on Entra-joined devices" if { lower(val) == "notallowed" }
build_message(val) := sprintf("Registering users are granted local admin rights on join (registeringUsers=%s)", [val])
