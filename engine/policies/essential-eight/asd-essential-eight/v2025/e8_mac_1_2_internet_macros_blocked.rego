# METADATA
# title: Ensure macros in files originating from the internet are blocked
# description: Ensure the "Block macros from running in Office files from the Internet" setting is enabled across Word, Excel and PowerPoint.
# related_resources:
# - ref: https://www.cyber.gov.au/resources-business-and-government/essential-cyber-security/essential-eight
#   description: ASD Essential Eight Maturity Model
# custom:
#   control_id: E8-MAC-1.2
#   framework: essential-eight
#   benchmark: asd-essential-eight
#   version: v2025
#   severity: high
#   service: Intune
#   maturity_level: ML1
#   requires_permissions:
#   - DeviceManagementConfiguration.Read.All

package essential_eight.asd_essential_eight.v2025.control_e8_mac_1_2

import rego.v1

default result := {
  "compliant": false,
  "message": "Unable to evaluate macro settings: no Intune Settings Catalog policy data available",
  "details": {},
}

# Per-app prefixes are inconsistent (PowerPoint is ppt16v2 in the prefix but
# 'powerpoint' in the category), so match on the leaf rather than rebuilding
# the full ID per app.
internet_block_leaf := "l_blockmacroexecutionfrominternet"

# This setting is flat: no child enum to descend into. The top-level value ends
# in _1 when the block is enabled.
enabled_suffix := "1"

required_apps := {"excel", "ppt", "word"}

app_display := {"excel": "Excel", "ppt": "PowerPoint", "word": "Word"}

# The worker passes the collector's return value straight to OPA, so the input is
# the collector output itself, with no wrapper around it.
input_present if {
  is_array(input.configuration_policies)
}

configuration_policies := object.get(input, "configuration_policies", [])

# Compare the last underscore-separated segment, not endswith: the setting ID
# itself ends in "...frominternet", so a suffix check would misread an
# unsuffixed value as enabled.
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

internet_block_settings contains entry if {
  some policy in configuration_policies
  some setting in object.get(policy, "settings", [])
  instance := object.get(setting, "settingInstance", {})
  definition_id := object.get(instance, "settingDefinitionId", "")
  contains(definition_id, internet_block_leaf)

  entry := {
    "app": app_of(definition_id),
    "policy_name": object.get(policy, "name", ""),
    "enabled": enum_suffix(object.get(instance, ["choiceSettingValue", "value"], "")) == enabled_suffix,
    "assigned": count(object.get(policy, "assignments", [])) > 0,
  }
}

# An unassigned policy reaches no device, so an enabled setting alone is not
# evidence of compliance. This does not prove per-device application, which needs
# the Intune reports API, but it rules out a policy that was never rolled out.
setting_compliant(entry) if {
  entry.enabled
  entry.assigned
}

apps_unassigned contains entry.app if {
  some entry in internet_block_settings
  not entry.assigned
}

configured_apps contains entry.app if {
  some entry in internet_block_settings
}

compliant_apps contains entry.app if {
  some entry in internet_block_settings
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
  "Macros in files originating from the internet are blocked for %s.",
  [concat(", ", labels(required_apps))],
) if {
  compliant
} else := sprintf(
  "Macros from internet-sourced files are not blocked for %d of %d required apps (%s). Not configured: %s. Present but not in force: %s.",
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
      "internet_block_settings_found": count(internet_block_settings),
      "compliant_apps": labels(compliant_apps & required_apps),
      "apps_not_configured": labels(apps_not_configured),
      "apps_misconfigured": labels(apps_misconfigured),
      "apps_unassigned": labels(apps_unassigned & required_apps),
      "settings_evidence": sort([e | some e in internet_block_settings]),
    },
  }
}
