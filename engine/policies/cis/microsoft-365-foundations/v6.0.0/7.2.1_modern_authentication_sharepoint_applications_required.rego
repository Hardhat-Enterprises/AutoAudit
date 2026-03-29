# METADATA
# title: Ensure modern authentication for SharePoint applications is required
# description: |
#   Modern authentication in SharePoint Online helps enforce stronger authentication
#   controls and reduces exposure to legacy protocols that do not support modern
#   security protections such as MFA and Conditional Access.
# related_resources:
# - ref: https://www.cisecurity.org/benchmark/microsoft_365
#   description: CIS Microsoft 365 Foundations Benchmark
# custom:
#   control_id: CIS-7.2.1
#   framework: cis
#   benchmark: microsoft-365-foundations
#   version: v6.0.0
#   severity: high
#   service: SharePoint
#   requires_permissions:
#   - SharePointTenantSettings.Read.All

package cis.microsoft_365_foundations.v6_0_0.control_7_2_1

default result := {"compliant": false, "message": "Evaluation failed"}

result := output if {
    legacy_auth_enabled := object.get(input, "legacy_auth_protocols_enabled", null)

    output := {
        "compliant": legacy_auth_enabled == false,
        "message": generate_message(legacy_auth_enabled),
        "affected_resources": generate_affected_resources(legacy_auth_enabled),
        "details": {
            "legacy_auth_protocols_enabled": legacy_auth_enabled
        }
    }
}

generate_message(legacy_auth_enabled) := "Legacy authentication protocols are disabled at the SharePoint tenant level" if {
    legacy_auth_enabled == false
}

generate_message(legacy_auth_enabled) := "Legacy authentication protocols are enabled at the SharePoint tenant level" if {
    legacy_auth_enabled == true
}

generate_message(legacy_auth_enabled) := "Unable to determine whether legacy authentication protocols are enabled at the SharePoint tenant level" if {
    legacy_auth_enabled == null
}

generate_affected_resources(false) := []

generate_affected_resources(true) := [
    "Legacy authentication protocols are enabled"
]

generate_affected_resources(null) := [
    "Legacy authentication protocol status unknown"
]
