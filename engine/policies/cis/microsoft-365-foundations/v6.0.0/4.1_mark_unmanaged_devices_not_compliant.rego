# METADATA
# title: Ensure devices without a compliance policy are marked 'not compliant'
# description: Mark devices without compliance policy as non-compliant.
# related_resources:
# - ref: https://learn.microsoft.com/en-us/mem/intune/protect/actions-for-noncompliance
#   description: Intune actions for noncompliance (conceptual)
# custom:
#   control_id: CIS-4.1
#   framework: cis
#   benchmark: microsoft-365-foundations
#   version: v6.0.0
#   severity: medium
#   service: Intune
#   requires_permissions:
#   - DeviceManagementConfiguration.Read.All

package cis.microsoft_365_foundations.v6_0_0.control_4_1

import rego.v1

default result := {
  "compliant": false,
  "message": "Unable to determine Intune compliance defaults",
  "details": {},
}

# Compliant when both secureByDefault and scheduled noncompliance actions are enabled.
compliant if {
  input.secure_by_default == true
  input.is_scheduled_action_enabled == true
}

compliant_value := true if { compliant } else := false if { true }

msg := "Devices without a compliance policy are treated as not compliant (secureByDefault & scheduled actions enabled)" if { compliant } else := "Intune compliance defaults are not sufficiently strict" if { true }

# Heuristic based on tenant settings:
# - secureByDefault should be true
# - isScheduledActionEnabled should be true (scheduled actions for noncompliance)
result := output if {
  secure_by_default := input.secure_by_default
  scheduled := input.is_scheduled_action_enabled

  output := {
    "compliant": compliant_value,
    "message": msg,
    "details": {
      "secure_by_default": secure_by_default,
      "is_scheduled_action_enabled": scheduled,
      "device_compliance_checkin_threshold_days": input.device_compliance_on_boarded,
      "compliance_policy_summaries_count": count(input.compliance_policy_summaries),
    },
  }
}

