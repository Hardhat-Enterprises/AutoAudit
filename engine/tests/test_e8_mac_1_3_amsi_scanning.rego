package essential_eight.asd_essential_eight.v2025.test_e8_mac_1_3

import rego.v1

amsi_setting_id := "user_vendor_msft_policy_config_office16v2~policy~l_microsoftofficesystem~l_securitysettings_l_macroruntimescanscope"


# ---------------------------------------------------------------------------
# Helpers: build minimal Settings Catalog data for the AMSI setting
# ---------------------------------------------------------------------------

amsi_setting(scope_value) := {
    "settingInstance": {
        "settingDefinitionId": amsi_setting_id,
        "choiceSettingValue": {
            "value": sprintf("%s_1", [amsi_setting_id]),
            "children": [
                {
                    "choiceSettingValue": {
                        "value": scope_value,
                    },
                },
            ],
        },
    },
}

configuration_policy(settings) := {
    "id": "policy-001",
    "name": "Microsoft Office macro security policy",
    "settings": settings,
}


# ---------------------------------------------------------------------------
# Test: compliant — AMSI scanning is enabled for low-trust documents
# ---------------------------------------------------------------------------

test_compliant_scope_1 if {
    result := data.essential_eight.asd_essential_eight.v2025.control_e8_mac_1_3.result with input as {
        "data": {
            "configuration_policies": [
                configuration_policy([
                    amsi_setting("amsi_scan_scope_1"),
                ]),
            ],
        },
    }

    result.compliant == true
    contains(result.message, "AMSI scanning is enabled")
}


# ---------------------------------------------------------------------------
# Test: compliant — AMSI scanning is enabled for all documents
# ---------------------------------------------------------------------------

test_compliant_scope_2 if {
    result := data.essential_eight.asd_essential_eight.v2025.control_e8_mac_1_3.result with input as {
        "data": {
            "configuration_policies": [
                configuration_policy([
                    amsi_setting("amsi_scan_scope_2"),
                ]),
            ],
        },
    }

    result.compliant == true
    contains(result.message, "AMSI scanning is enabled")
}


# ---------------------------------------------------------------------------
# Test: non-compliant — nested scope has an unsupported value
# ---------------------------------------------------------------------------

test_non_compliant_invalid_scope if {
    result := data.essential_eight.asd_essential_eight.v2025.control_e8_mac_1_3.result with input as {
        "data": {
            "configuration_policies": [
                configuration_policy([
                    amsi_setting("amsi_scan_scope_0"),
                ]),
            ],
        },
    }

    result.compliant == false
    contains(result.message, "not enabled")
}


# ---------------------------------------------------------------------------
# Test: non-compliant — AMSI setting is missing
# ---------------------------------------------------------------------------

test_non_compliant_missing_setting if {
    result := data.essential_eight.asd_essential_eight.v2025.control_e8_mac_1_3.result with input as {
        "data": {
            "configuration_policies": [
                configuration_policy([]),
            ],
        },
    }

    result.compliant == false
    contains(result.message, "not enabled")
}