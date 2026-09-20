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


required_applications := {"Word", "Excel", "PowerPoint"}


default result := {
  "compliant": false,
  "message": "Unable to determine whether Office macro settings are enforced by policy",
  "details": {},
}


# At least one VBA Macro Notification Setting must have been discovered.
settings_found if {
  input.macro_settings_found == true
  is_array(input.settings)
  count(input.settings) > 0
}


# A setting is considered centrally enforced only when its Intune policy is
# enabled and assigned to at least one target.
setting_enforced(setting) if {
  setting.state == "enabled"
  setting.assigned == true
}


# Required applications for which a VBA Macro Notification Setting exists.
configured_applications contains application if {
  some setting in input.settings
  application := setting.application
  application in required_applications
}


# Required applications with at least one enabled and assigned policy.
enforced_applications contains application if {
  some setting in input.settings
  application := setting.application
  application in required_applications
  setting_enforced(setting)
}


# Required applications with at least one discovered but unassigned policy.
unassigned_applications contains application if {
  some setting in input.settings
  application := setting.application
  application in required_applications
  setting.assigned == false
}


# Required applications that do not have an enabled and assigned policy.
missing_applications := required_applications - enforced_applications


# Required applications for which no VBA Macro Notification Setting was found.
not_configured_applications := required_applications - configured_applications


# Required applications that have a setting but no setting currently in force.
misconfigured_applications := missing_applications - not_configured_applications


# Compliance requires Word, Excel, and PowerPoint each to have at least one
# enabled and assigned VBA Macro Notification Settings policy.
compliant if {
  settings_found
  count(missing_applications) == 0
}


compliant_value := true if {
  compliant
} else := false if {
  true
}


msg := "Office macro security settings are enabled, assigned, and enforced for Word, Excel, and PowerPoint" if {
  compliant
} else := "Office macro security settings are not fully enforced for Word, Excel, and PowerPoint" if {
  true
}


result := output if {
  output := {
    "compliant": compliant_value,
    "message": msg,
    "details": {
      "macro_settings_found": input.macro_settings_found,
      "settings": input.settings,
      "configured_applications": sort([app | some app in configured_applications]),
      "enforced_applications": sort([app | some app in enforced_applications]),
      "missing_applications": sort([app | some app in missing_applications]),
      "not_configured_applications": sort([app | some app in not_configured_applications]),
      "misconfigured_applications": sort([app | some app in misconfigured_applications]),
      "unassigned_applications": sort([app | some app in unassigned_applications]),
      "source": input.source,
      "total_policies_checked": input.total_policies_checked,
    },
  }
}