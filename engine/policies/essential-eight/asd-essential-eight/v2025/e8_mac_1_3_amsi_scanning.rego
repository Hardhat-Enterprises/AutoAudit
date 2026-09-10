# METADATA
# title: Ensure AMSI scanning is enabled for Office macros
# description: Ensure Microsoft Office macros are scanned by AMSI before execution.
# custom:
#   control_id: E8-MAC-1.3
#   framework: essential-eight
#   benchmark: asd-essential-eight
#   version: v2025
#   severity: high
#   service: Intune
#   maturity_level: ML1
#   requires_permissions:
#   - DeviceManagementConfiguration.Read.All

package essential_eight.asd_essential_eight.v2025.control_e8_mac_1_3

import rego.v1

amsi_setting_id := "user_vendor_msft_policy_config_office16v2~policy~l_microsoftofficesystem~l_securitysettings_l_macroruntimescanscope"

default result := {
  "compliant": false,
  "message": "AMSI macro scanning setting was not found or is not compliant",
  "details": {},
}

# The top-level value only shows that the policy is enabled.
# The actual AMSI scan scope is stored in:
# choiceSettingValue.children[0].choiceSettingValue.value

nested_scope_value(setting) := value if {
  value := setting.settingInstance.choiceSettingValue.children[0].choiceSettingValue.value
}

is_amsi_setting(setting) if {
  setting.settingInstance.settingDefinitionId == amsi_setting_id
}

is_compliant_scope(value) if {
  endswith(value, "_1")
}

is_compliant_scope(value) if {
  endswith(value, "_2")
}

compliant_setting(setting) if {
  is_amsi_setting(setting)
  value := nested_scope_value(setting)
  is_compliant_scope(value)
}

compliant if {
  some policy in input.configuration_policies
  some setting in policy.settings
  compliant_setting(setting)
}

compliant_value := true if {
  compliant
} else := false if {
  true
}

message := "AMSI scanning is enabled for Office macros" if {
  compliant
} else := "AMSI scanning is not enabled with a compliant scan scope" if {
  true
}

result := {
  "compliant": compliant_value,
  "message": message,
  "details": {
    "setting_id": amsi_setting_id,
  },
}