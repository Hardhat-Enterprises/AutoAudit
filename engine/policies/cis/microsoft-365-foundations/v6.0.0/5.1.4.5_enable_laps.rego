# METADATA
# title: Ensure Local Administrator Password Solution is enabled
# description: Ensure Microsoft Entra Local Administrator Password Solution (LAPS) is enabled
# control_id: CIS-5.1.4.5
# framework: cis
# benchmark: microsoft-365-foundations
# version: v6.0.0
# severity: high
# service: EntraID
# requires_permissions:
#   - Policy.Read.DeviceConfiguration

package cis.microsoft_365_foundations.v6_0_0.control_5_1_4_5

default result := {
    "compliant": false,
    "message": "Unable to determine whether LAPS is enabled",
    "details": {}
}

compliant if {
    input.laps_enabled == true
}

compliant_value := true if {
    compliant
} else := false if {
    true
}

msg := "Microsoft Entra Local Administrator Password Solution (LAPS) is enabled" if {
    compliant
} else := "Microsoft Entra Local Administrator Password Solution (LAPS) is not enabled"

result := output if {
    output := {
        "compliant": compliant_value,
        "message": msg,
        "details": {
            "laps_enabled": input.laps_enabled,
            "local_admin_password_settings": input.local_admin_password_settings
        }
    }
}