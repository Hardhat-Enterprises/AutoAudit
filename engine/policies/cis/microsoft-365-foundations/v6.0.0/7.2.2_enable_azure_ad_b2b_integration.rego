# METADATA
# title: Ensure SharePoint and OneDrive integration with Azure AD B2B is enabled
# description: |
#   Enabling Azure AD B2B integration for SharePoint and OneDrive ensures
#   that external users are managed through Microsoft Entra ID B2B.
#   This provides more consistent authentication, access control, and
#   lifecycle management for guest users.
# related_resources:
# - ref: https://www.cisecurity.org/benchmark/microsoft_365
#   description: CIS Microsoft 365 Foundations Benchmark
# custom:
#   control_id: CIS-7.2.2
#   framework: cis
#   benchmark: microsoft-365-foundations
#   version: v6.0.0
#   severity: medium
#   service: SharePoint
#   requires_permissions:
#   - SharePointTenantSettings.Read.All

package cis.microsoft_365_foundations.v6_0_0.control_7_2_2

default result := {
    "compliant": false,
    "message": "Evaluation failed"
}

result := output if {
    b2b_integration_enabled := input.azure_ad_b2b_integration_enabled

    compliant := b2b_integration_enabled == true

    output := {
        "compliant": compliant,
        "message": generate_message(b2b_integration_enabled),
        "affected_resources": generate_affected_resources(compliant),
        "details": {
            "azure_ad_b2b_integration_enabled": b2b_integration_enabled
        }
    }
}

generate_message(b2b_integration_enabled) := msg if {
    b2b_integration_enabled == true
    msg := "SharePoint and OneDrive integration with Azure AD B2B is enabled"
}

generate_message(b2b_integration_enabled) := msg if {
    b2b_integration_enabled == false
    msg := "SharePoint and OneDrive integration with Azure AD B2B is disabled"
}

generate_message(b2b_integration_enabled) := msg if {
    b2b_integration_enabled == null
    msg := "Unable to determine SharePoint and OneDrive Azure AD B2B integration status"
}

generate_affected_resources(true) := []

generate_affected_resources(false) := [
    "SharePoint and OneDrive Azure AD B2B integration is disabled"
]