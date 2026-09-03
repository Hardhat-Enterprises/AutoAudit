# METADATA
# title: Ensure users cannot change macro settings
# description: Ensure Microsoft Office macro security settings are enforced so standard users cannot override or modify the configured macro settings.
# related_resources:
# - ref: https://www.cyber.gov.au/resources-business-and-government/essential-cyber-security/essential-eight
#   description: ASD Essential Eight Maturity Model
# custom:
#   control_id: E8-MAC-1.4
#   framework: essential-eight
#   benchmark: asd-essential-eight
#   version: v2025
#   severity: medium
#   service: Intune
#   maturity_level: ML1
#   requires_permissions:
#   - DeviceManagementConfiguration.Read.All

package essential_eight.asd_essential_eight.v2025.control_e8_mac_1_4

import rego.v1


default result := {
  "compliant": false,
  "message": "Unable to determine whether Office macro settings are enforced by policy",
  "details": {},
}


# At least one VBA Macro Notification Setting must have been discovered.
settings_found if {
  input.macro_settings_found == true
  count(input.settings) > 0
}


# A discovered setting is considered centrally configured when its
# VBA Macro Notification Settings policy has an explicit policy state.
setting_enforced(setting) if {
  setting.state == "enabled"
}

setting_enforced(setting) if {
  setting.state == "disabled"
}


# Find settings whose state could not be confirmed as centrally configured.
invalid_settings contains setting if {
  some setting in input.settings
  not setting_enforced(setting)
}


# Compliant when VBA Macro Notification Settings were discovered and every
# discovered setting has an explicit policy-controlled state.
compliant if {
  settings_found
  count(invalid_settings) == 0
}


compliant_value := true if {
  compliant
} else := false if {
  true
}


msg := "Office macro security settings are enforced by policy" if {
  compliant
} else := "Office macro security settings could not be confirmed as enforced by policy" if {
  true
}


result := output if {
  output := {
    "compliant": compliant_value,
    "message": msg,
    "details": {
      "macro_settings_found": input.macro_settings_found,
      "settings": input.settings,
      "source": input.source,
      "total_policies_checked": input.total_policies_checked,
    },
  }
}