# METADATA
# title: Ensure Win32 API calls from Office macros are blocked
# description: Ensure the Attack Surface Reduction rule blocking Win32 API calls from Office macros is enabled in Block mode.
# related_resources:
# - ref: https://www.cyber.gov.au/resources-business-and-government/essential-cyber-security/essential-eight
#   description: ASD Essential Eight Maturity Model
# custom:
#   control_id: E8-MAC-2.1
#   framework: essential-eight
#   benchmark: asd-essential-eight
#   version: v2025
#   severity: high
#   service: Intune
#   maturity_level: ML2
#   requires_permissions:
#   - DeviceManagementConfiguration.Read.All

package essential_eight.asd_essential_eight.v2025.control_e8_mac_2_1

import rego.v1

default result := {
  "compliant": false,
  "message": "Unable to determine Win32 API macro blocking rule state",
  "details": {},
}

compliant if {
  input.win32_api_rule_state == "block"
}

compliant_value := true if { compliant } else := false if { true }

msg := "Win32 API calls from Office macros are blocked in Block mode" if {
  compliant
} else := sprintf(
  "Win32 API macro blocking is not compliant. Current state is '%s'; Essential Eight requires Block mode.",
  [input.win32_api_rule_state],
) if { true }

result := output if {
  output := {
    "compliant": compliant_value,
    "message": msg,
    "details": {
      "win32_api_rule_state": input.win32_api_rule_state,
      "win32_api_rule_found": input.win32_api_rule_found,
      "source": input.source,
      "policy_name": input.policy_name,
    },
  }
}
