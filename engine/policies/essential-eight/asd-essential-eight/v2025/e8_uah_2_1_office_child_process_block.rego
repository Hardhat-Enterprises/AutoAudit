# METADATA
# title: Ensure Microsoft Office applications are blocked from creating child processes
# description: Ensure the Attack Surface Reduction rule blocking Office applications from creating child processes is enabled in Block mode.
# related_resources:
# - ref: https://www.cyber.gov.au/resources-business-and-government/essential-cyber-security/essential-eight/essential-eight-maturity-model
#   description: ASD Essential Eight Maturity Model
# - ref: https://learn.microsoft.com/en-us/compliance/anz/e8-app-harden
#   description: Microsoft's ISM/Essential Eight control mapping for User Application Hardening (ISM-1667)
# custom:
#   control_id: E8-UAH-2.1
#   framework: essential-eight
#   benchmark: asd-essential-eight
#   version: v2025
#   severity: high
#   service: Intune
#   maturity_level: ML2
#   requires_permissions:
#   - DeviceManagementConfiguration.Read.All

package essential_eight.asd_essential_eight.v2025.control_e8_uah_2_1

import rego.v1

default result := {
  "compliant": false,
  "message": "Unable to determine Office child-process blocking rule state",
  "details": {},
}

compliant if {
  input.office_child_process_rule_state == "block"
}

compliant_value := true if { compliant } else := false if { true }

msg := "Office applications are blocked from creating child processes (Block mode)" if {
  compliant
} else := sprintf(
  "Office child-process blocking is not compliant. Current state is '%s'; Essential Eight requires Block mode.",
  [input.office_child_process_rule_state],
) if { true }

result := output if {
  output := {
    "compliant": compliant_value,
    "message": msg,
    "details": {
      "office_child_process_rule_state": input.office_child_process_rule_state,
      "office_child_process_rule_found": input.office_child_process_rule_found,
      "source": input.office_child_process_source,
      "policy_name": input.office_child_process_policy_name,
    },
  }
}
