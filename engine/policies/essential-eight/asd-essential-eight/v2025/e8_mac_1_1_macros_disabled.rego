# METADATA
# title: Ensure Office macros are disabled for users without a business requirement
# description: Ensure the VBA Macro Notification Setting disables macros by default across Word, Excel and PowerPoint.
# related_resources:
# - ref: https://www.cyber.gov.au/resources-business-and-government/essential-cyber-security/essential-eight
#   description: ASD Essential Eight Maturity Model
# custom:
#   control_id: E8-MAC-1.1
#   framework: essential-eight
#   benchmark: asd-essential-eight
#   version: v2025
#   severity: high
#   service: Intune
#   maturity_level: ML1
#   requires_permissions:
#   - DeviceManagementConfiguration.Read.All

package essential_eight.asd_essential_eight.v2025.control_e8_mac_1_1

import rego.v1

default result := {
  "compliant": false,
  "message": "Unable to evaluate macro settings: no Intune Settings Catalog policy data available",
  "details": {},
}

# Match on the leaf. Per-app prefixes are inconsistent (PowerPoint is ppt16v2 in
# the prefix but 'powerpoint' in the category), so the full ID cannot be rebuilt
# from a single {app} substitution.
vba_leaf := "l_vbawarningspolicy"

# Trailing enum on the child value: 2 = disable with notification, 4 = disable
# without. 3 (signed macros only) is accepted because maturity levels are
# cumulative; E8-MAC-3.1 is the strict check for 3.
compliant_levels := {"2", "3", "4"}

required_apps := {"excel", "ppt", "word"}

app_display := {"excel": "Excel", "ppt": "PowerPoint", "word": "Word"}

# The worker passes the collector's return value straight to OPA, so there is no
# 'data' wrapper here - that exists only in files saved by scripts/test_collector.
input_present if {
  is_array(input.configuration_policies)
}

configuration_policies := object.get(input, "configuration_policies", [])

# Values encode the selection as a trailing "_<enum>". Compare the last segment
# rather than using endswith, since the ID itself can end in a digit.
enum_suffix(value) := suffix if {
  parts := split(value, "_")
  suffix := parts[count(parts) - 1]
}

app_of(definition_id) := app if {
  prefix := split(definition_id, "~")[0]
  app := trim_suffix(trim_prefix(prefix, "user_vendor_msft_policy_config_"), "16v2")
}

app_label(app) := object.get(app_display, app, app)

labels(apps) := sort([app_label(a) | some a in apps])

list_or_none(apps) := "none" if {
  count(apps) == 0
} else := concat(", ", labels(apps))

# The top-level value only means "policy Enabled"; the macro level itself is in
# children[0]. The child's own settingDefinitionId varies per app, so only its
# value is read.
selected_level(instance) := level if {
  children := object.get(instance, ["choiceSettingValue", "children"], [])
  count(children) > 0
  level := enum_suffix(object.get(children[0], ["choiceSettingValue", "value"], ""))
} else := "unset"

vba_settings contains entry if {
  some policy in configuration_policies
  some setting in object.get(policy, "settings", [])
  instance := object.get(setting, "settingInstance", {})
  definition_id := object.get(instance, "settingDefinitionId", "")
  contains(definition_id, vba_leaf)

  entry := {
    "app": app_of(definition_id),
    "policy_name": object.get(policy, "name", ""),
    "policy_enabled": enum_suffix(object.get(instance, ["choiceSettingValue", "value"], "")) == "1",
    "level": selected_level(instance),
  }
}

setting_compliant(entry) if {
  entry.policy_enabled
  entry.level in compliant_levels
}

configured_apps contains entry.app if {
  some entry in vba_settings
}

compliant_apps contains entry.app if {
  some entry in vba_settings
  setting_compliant(entry)
}

missing_apps := required_apps - compliant_apps

apps_not_configured := required_apps - configured_apps

apps_misconfigured := missing_apps - apps_not_configured

compliant if {
  count(missing_apps) == 0
}

compliant_value := true if { compliant } else := false if { true }

msg := sprintf(
  "Office macros are disabled by default for %s, each with a compliant VBA Macro Notification level.",
  [concat(", ", labels(required_apps))],
) if {
  compliant
} else := sprintf(
  "Office macros are not disabled by default for %d of %d required apps (%s). Not configured: %s. Configured at a non-compliant level: %s.",
  [
    count(missing_apps),
    count(required_apps),
    list_or_none(missing_apps),
    list_or_none(apps_not_configured),
    list_or_none(apps_misconfigured),
  ],
) if { true }

result := output if {
  input_present

  output := {
    "compliant": compliant_value,
    "message": msg,
    "details": {
      "total_configuration_policies": count(configuration_policies),
      "vba_settings_found": count(vba_settings),
      "compliant_apps": labels(compliant_apps & required_apps),
      "apps_not_configured": labels(apps_not_configured),
      "apps_misconfigured": labels(apps_misconfigured),
      "settings_evidence": sort([e | some e in vba_settings]),
    },
  }
}
