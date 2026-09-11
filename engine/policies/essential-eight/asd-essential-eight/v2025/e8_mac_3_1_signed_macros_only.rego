# METADATA
# title: Ensure only digitally signed macros from trusted publishers can execute
# description: Ensure the VBA Macro Notification Setting is set to "Disable all except digitally signed macros" across Word, Excel and Powerpoint (ML3 tightening of E8-MAC-1.1)
# related_resources:
# - ref: https://www.cyber.gov.au/resources-business-and-government/essential-cyber-security/essential-eight
#   description: ASD Essential Eight Maturity Model
# custom:
#   control_id: E8-MAC-3.1
#   framework: essential_eight
#   benchmark: asd_essential_eight
#   version: v2025
#   severity: high
#   service: Intune
#   maturity_level: ML3
#   requires_permissions:
#   - DeviceManagementConfiguration.Read.All

package essential_eight.asd_essential_eight.v2025.control_e8_mac_3_1

import rego.v1

#Fallback result if input is missing/malformed.
default result := {
    "compliant": false,
    "message": "Unable to evaluate signed-macros setting: no Intune Settings Catalog Policy data available",
    "details": {},
}

# --Matching constants--

# Match on the leaf only, not the full ID. Per-app prefixes are inconsistent.
# Powerpoint's prefix is "ppt16v2" but its category says "powerpoint"
# There's no clean {app} substitution that rebuilds the full string
# Using 'contains' on the leaf sidesteps that.
vba_leaf := "l_vbawarningspolicy"

# Enum "3" on the nested child value = "disable all except digitally signed macros"
# is the only setting that satisfies ML3.
# Unlike E8-MAC-1.1, which accepts {"2","3","4"} as baseline, this control is strict check,
# so only "3" counts.
complaint_levels := {"3"}

# The three office apps this controller covers
required_apps := {"excel", "ppt", "word"}

# Readable messages - maps internal keys to display names
app_display := {"excel": "Excel", "ppt": "PowerPoint", "word": "Word"}


# ---Guard Logic for malformed or wrapped input---

# The worker hands us the collector's output directly, so there's no data wrapper at runtime.
# A data wrapper only shows up in fixture files saved by engine/scripts/test_collector.py.
# This check confirms we got the shape we expect before we try to evaluate it.
input_present if {
    is_array(input.configuration_policies)
}

# Fallback to an empty list if the field's missing or wrong type,
# bad payload degrades gracefully instead of blowing up mid-evaluation.
configuration_policies := object.get(input, "configuration_policies", [])


# ----Nested Value Extraction----

# The top level choiceSettingValue only tells us the policy is Enabled
# the actual VBA warning level lives one step down, in the first child's value
# encoded as a trailing "_<enum>".
# We split on "_" and take the last segment rather than using endswith()
# because setting ID itself can end in a digit.
enum_suffix(value)  := suffix if {
    parts := split(value, "_")
    suffix := parts[count(parts) - 1]
}

# Extracts the app key (excel/ppt/word) from settingDefinitionId's prefixe
# by trimming off its first "~" delimited segment.
app_of(definition_id) := app if {
    prefix := split(definition_id, "~")[0]
    app := trim_suffix(trim_prefix(prefix, "user_vendor_msft_policy_config_"), "16v2")
}

app_label(app) := object.get(app_display, app, app)

labels(apps) := sort([app_label(a) | some a in apps])

list_or_none(apps) := "none" if {
    count(apps) == 0
} else := concat(", ", labels(apps))

# Reads the actual VBA level from children[0].
# No child usually means the setting was never expanded,
# so we call it "unset" instead of failing.
selected_level(instance) := level if {
    children := object.get(instance, ["choiceSettingValue", "children"], [])
    count(children) > 0
    level := enum_suffix(object.get(children[0], ["choiceSettingValue", "value"], ""))
} else := "unset"


# -----Evidence collection across policies-----

# Scans every policy for the VBA leaf or setting pair
# and captures what we need to judge each app:
# is the policy on,
# what level is it set to,
# is it actually assigned
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
        "assigned": count(object.get(policy, "assignments", [])) > 0,
        "level": selected_level(instance),
    }
}


# -----Complaince Rules-----

# Compliant only if the policy is on, locked to level 3, and assigned.
# A correct but unassigned policy reaches no device, so it doesn't count.
setting_compliant(entry) if {
    entry.policy_enabled
    entry.level in complaint_levels
    entry.assigned
}

# Called out seperately since the fix is an assignment, and not a configuration change
apps_unassigned contains entry.app if {
    some entry in vba_settings
    not entry.assigned
}

configured_apps contains entry.app if {
    some entry in vba_settings
}

compliant_apps contains entry.app if {
    some entry in vba_settings
    setting_compliant(entry)
}

missing_apps = required_apps - compliant_apps

unconfigured_apps = required_apps - configured_apps

misconfigured_apps := missing_apps - unconfigured_apps


# ------Results------

compliant if {
    count(missing_apps) == 0
}

# Rego has no ternary,
# the standard way to collapse a boolean rule into plain true/false
compliant_value := true if {compliant} else := false if { true }

msg := sprintf(
    "Only digitally signed macros ffrom trusted publishers can execute for %s.",
    [concat(", ", labels(required_apps))],
) if {
    compliant
} else := sprintf(
    "Signed Macros Only is not enforced for %d of %d required apps (%s). \nNot configured: %s. \nPresent but not compliant: %s.",
    [
        count(missing_apps),
        count(required_apps),
        list_or_none(missing_apps),
        list_or_none(unconfigured_apps),
        list_or_none(misconfigured_apps),
    ],
) if { true }

# Only overrides the default result when input is well-formed.
# If input_present is false, this never fires and the safe default result stands.
result := output if {
    input_present

    output := {
        "compliant": compliant_value,
        "message": msg,
        "details": {
            "total_configuration_policies": count(configuration_policies),
            "vba_settings_found": count(vba_settings),
            "compliant_apps": labels(compliant_apps & required_apps),
            "apps_not_configured": labels(unconfigured_apps),
            "apps_misconfigured": labels(misconfigured_apps),
            "apps_unassigned": labels(apps_unassigned & required_apps),
            "settings_evidence": sort([e | some e in vba_settings]),
        },
    }
}
