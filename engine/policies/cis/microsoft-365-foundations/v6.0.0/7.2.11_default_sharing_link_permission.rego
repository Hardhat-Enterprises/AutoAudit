# METADATA
# title: Ensure the SharePoint default sharing link permission is set
# description: |
#   Ensures the default permission selected for SharePoint sharing links
#   is set to View.
# related_resources:
# - ref: https://www.cisecurity.org/benchmark/microsoft_365
#   description: CIS Microsoft 365 Foundations Benchmark
# custom:
#   control_id: CIS-7.2.11
#   framework: cis
#   benchmark: microsoft-365-foundations
#   version: v6.0.0
#   severity: medium
#   service: SharePoint
#   requires_permissions:
#   - SharePoint.Admin

package cis.microsoft_365_foundations.v6_0_0.control_7_2_11

default result := {"compliant": false, "message": "Evaluation failed"}

result := output if {
    tenant := object.get(input, "tenant", {})
    default_link_permission := object.get(
        tenant,
        "DefaultLinkPermission",
        null
    )

    compliant := default_link_permission == 1

    output := {
        "compliant": compliant,
        "message": generate_message(default_link_permission),
        "affected_resources": generate_affected_resources(compliant),
        "details": {
            "default_link_permission": default_link_permission
        }
    }
}

generate_message(default_link_permission) := msg if {
    default_link_permission == 1
    msg := "SharePoint default sharing link permission is set to View"
}

generate_message(default_link_permission) := msg if {
    default_link_permission == 0
    msg := "SharePoint default sharing link permission is None instead of View"
}

generate_message(default_link_permission) := msg if {
    default_link_permission == 2
    msg := "SharePoint default sharing link permission is Edit instead of View"
}

generate_message(default_link_permission) := msg if {
    default_link_permission != null
    default_link_permission != 0
    default_link_permission != 1
    default_link_permission != 2
    msg := sprintf(
        "Unknown SharePoint default sharing link permission value: %v",
        [default_link_permission]
    )
}

generate_message(default_link_permission) := msg if {
    default_link_permission == null
    msg := "Unable to determine SharePoint default sharing link permission"
}

generate_affected_resources(true) := []
generate_affected_resources(false) := ["SharePoint default sharing link permission"]
