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
#   data_collector_id: sharepoint.pnp.tenant
#   requires_permissions:
#   - SharePoint.Admin

package cis.microsoft_365_foundations.v6_0_0.control_7_2_5

default result := {
    "compliant": false,
    "message": "Evaluation failed"
}

result := output if {
    prevent_resharing := input.prevent_external_users_from_resharing

    compliant := prevent_resharing == true

    output := {
        "compliant": compliant,
        "message": generate_message(prevent_resharing),
        "affected_resources": generate_affected_resources(compliant),
        "details": {
            "prevent_external_users_from_resharing": prevent_resharing
        }
    }
}

generate_message(prevent_resharing) := msg if {
    prevent_resharing == true
    msg := "SharePoint guest users cannot reshare items they do not own"
}

generate_message(prevent_resharing) := msg if {
    prevent_resharing == false
    msg := "SharePoint guest users can reshare items they do not own"
}

generate_message(prevent_resharing) := msg if {
    prevent_resharing == null
    msg := "Unable to determine whether SharePoint guest users can reshare items they do not own"
}

generate_affected_resources(true) := []

generate_affected_resources(false) := [
    "SharePoint guest users are allowed to reshare items they do not own"
]