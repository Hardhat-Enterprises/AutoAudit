# METADATA
# title: Ensure device enrollment for personally owned devices is blocked by default
# description: Block personal device enrollment by default.
# related_resources:
# - ref: https://www.cisecurity.org/benchmark/microsoft_365
#   description: CIS Microsoft 365 Foundations Benchmark
# custom:
#   control_id: CIS-4.2
#   framework: cis
#   benchmark: microsoft-365-foundations
#   version: v6.0.0
#   severity: medium
#   service: Intune
#   requires_permissions:
#   - DeviceManagementServiceConfig.Read.All

package cis.microsoft_365_foundations.v6_0_0.control_4_2

import rego.v1

default result := {
  "compliant": false,
  "message": "Unable to determine personal device enrollment restriction",
  "details": {},
}

compliant_value := true if { input.personal_devices_blocked == true } else := false if { true }

msg := "Personal device enrollment is blocked by default" if { input.personal_devices_blocked == true } else := "Personal device enrollment is not blocked by default" if { input.personal_devices_blocked == false } else := "Unable to determine personal device enrollment restriction" if { true }

result := output if {
  blocked := input.personal_devices_blocked

  output := {
    "compliant": compliant_value,
    "message": msg,
    "details": {
      "personal_devices_blocked": blocked,
      "total_configurations": input.total_configurations,
      "platform_restrictions_count": count(input.platform_restrictions),
    },
  }
}

