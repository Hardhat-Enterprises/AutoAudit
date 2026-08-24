# METADATA
# title: Ensure that SharePoint guest users cannot share items they don't own
# description: |
#   Restricting guest users from resharing content they do not own helps
#   prevent unintended sharing of SharePoint and OneDrive resources.
# related_resources:
# - ref: https://www.cisecurity.org/benchmark/microsoft_365
#   description: CIS Microsoft 365 Foundations Benchmark
# custom:
#   control_id: CIS-7.2.5
#   framework: cis
#   benchmark: microsoft-365-foundations
#   version: v6.0.0
#   severity: medium
#   service: SharePoint
#   requires_permissions:
#   - SharePointTenantSettings.Read.All

package cis.microsoft_365_foundations.v6_0_0.control_7_2_5

default result := {
    "compliant": false,
    "message": "Evaluation failed"
}

result := output if {
    resharing_enabled := input.is_resharing_by_external_users_enabled

    compliant := resharing_enabled == false

    output := {
        "compliant": compliant,
        "message": generate_message(resharing_enabled),
        "affected_resources": generate_affected_resources(compliant),
        "details": {
            "is_resharing_by_external_users_enabled": resharing_enabled
        }
    }
}

generate_message(resharing_enabled) := msg if {
    resharing_enabled == false
    msg := "SharePoint guest users cannot reshare items they do not own"
}

generate_message(resharing_enabled) := msg if {
    resharing_enabled == true
    msg := "SharePoint guest users can reshare items they do not own"
}

generate_message(resharing_enabled) := msg if {
    resharing_enabled == null
    msg := "Unable to determine whether SharePoint guest users can reshare items they do not own"
}

generate_affected_resources(true) := []

generate_affected_resources(false) := [
    "SharePoint guest users are allowed to reshare items they do not own"
]