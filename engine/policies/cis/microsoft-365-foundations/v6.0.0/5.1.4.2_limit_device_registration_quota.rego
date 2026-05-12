# METADATA
# title: Ensure the maximum number of devices per user is limited
# description: |
#   Setting an upper bound on device registrations per user reduces the attack
#   surface from compromised accounts and limits lateral movement via registered
#   devices. CIS recommends setting this to 5.
# related_resources:
# - ref: https://www.cisecurity.org/benchmark/microsoft_365
#   description: CIS Microsoft 365 Foundations Benchmark
# custom:
#   control_id: CIS-5.1.4.2
#   framework: cis
#   benchmark: microsoft-365-foundations
#   version: v6.0.0
#   severity: medium
#   service: EntraID
#   requires_permissions:
#   - Policy.Read.DeviceConfiguration

package cis.microsoft_365_foundations.v6_0_0.control_5_1_4_2

import rego.v1

default result := {
    "compliant": false,
    "message": "Evaluation failed: unable to retrieve device registration policy",
    "details": {},
}

compliant := true if {
    input.user_device_quota != null
    input.user_device_quota > 0
    input.user_device_quota <= 20
} else := false

result := output if {
    quota := input.user_device_quota
    output := {
        "compliant": compliant,
        "message": build_message(quota),
        "affected_resources": [],
        "details": {"user_device_quota": quota},
    }
}

build_message(q) := "Device registration quota is not configured" if {
    q == null
} else := "Device registration quota is set to unlimited (non-compliant; CIS requires 20 or less)" if {
    q == 0
} else := sprintf("Device registration quota is set to %d", [q]) if {
    q <= 20
} else := sprintf("Device registration quota is %d; CIS requires 20 or less", [q])
