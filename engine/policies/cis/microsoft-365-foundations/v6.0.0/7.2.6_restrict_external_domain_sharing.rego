```rego
# METADATA
# title: Ensure SharePoint external sharing is restricted
# description: |
#   Restricting SharePoint and OneDrive external sharing to approved domains
#   helps prevent users from sharing organizational data with unauthorized
#   external domains.
# related_resources:
# - ref: https://www.cisecurity.org/benchmark/microsoft_365
#   description: CIS Microsoft 365 Foundations Benchmark
# custom:
#   control_id: CIS-7.2.6
#   framework: cis
#   benchmark: microsoft-365-foundations
#   version: v6.0.0
#   severity: medium
#   service: SharePoint
#   data_collector_id: sharepoint.pnp.tenant
#   requires_permissions:
#   - SharePoint.Admin

package cis.microsoft_365_foundations.v6_0_0.control_7_2_6

default result := {
    "compliant": false,
    "message": "Evaluation failed"
}

result := output if {
    restriction_mode := input.restrict_external_domain_sharing

    compliant := restriction_mode == "AllowList"

    output := {
        "compliant": compliant,
        "message": generate_message(restriction_mode),
        "affected_resources": generate_affected_resources(compliant),
        "details": {
            "restrict_external_domain_sharing": restriction_mode
        }
    }
}

generate_message(restriction_mode) := msg if {
    restriction_mode == "AllowList"
    msg := "SharePoint external sharing is restricted to approved domains"
}

generate_message(restriction_mode) := msg if {
    restriction_mode != "AllowList"
    restriction_mode != null
    msg := sprintf(
        "SharePoint external sharing is not restricted using an allow list. Current mode: %s",
        [restriction_mode]
    )
}

generate_message(restriction_mode) := msg if {
    restriction_mode == null
    msg := "Unable to determine the SharePoint external domain sharing restriction mode"
}

generate_affected_resources(true) := []

generate_affected_resources(false) := [
    "SharePoint external sharing is not restricted to approved domains"
]
```
