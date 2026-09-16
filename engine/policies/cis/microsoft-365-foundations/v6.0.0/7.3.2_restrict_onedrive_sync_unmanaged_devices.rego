# METADATA
# title: Ensure OneDrive sync is restricted for unmanaged devices
# description: |
#   Restricts OneDrive synchronization from unmanaged devices.
# related_resources:
# - ref: https://www.cisecurity.org/benchmark/microsoft_365
#   description: CIS Microsoft 365 Foundations Benchmark
# custom:
#   control_id: CIS-7.3.2
#   framework: cis
#   benchmark: microsoft-365-foundations
#   version: v6.0.0
#   severity: medium
#   service: SharePoint
#   requires_permissions:
#   - SharePoint.Admin

package cis.microsoft_365_foundations.v6_0_0.control_7_3_2

default result := {
    "compliant": false,
    "message": "Evaluation failed: unable to determine OneDrive sync client restriction status",
    "affected_resources": [],
    "details": {}
}

result := output if {
    restricted := object.get(
        input,
        "is_unmanaged_sync_client_for_tenant_restricted",
        null
    )

    restricted != null

    domains := object.get(input, "allowed_domain_list", [])
    domain_count := count(domains)

    compliant := is_restricted(restricted, domain_count)

    output := {
        "compliant": compliant,
        "message": generate_message(restricted, domain_count),
        "affected_resources": generate_affected_resources(compliant),
        "details": {
            "is_unmanaged_sync_client_for_tenant_restricted": restricted,
            "allowed_domain_list": domains,
            "allowed_domain_count": domain_count
        }
    }
}

# CIS 7.3.2 requires the restriction to be enabled and at least one
# allowed domain GUID to be configured. The policy cannot verify that
# the configured GUIDs are the organisation's correct trusted domains,
# so the domain list is returned in details for human review.
is_restricted(restricted, domain_count) := true if {
    restricted == true
    domain_count > 0
} else := false

generate_message(restricted, domain_count) := msg if {
    restricted == true
    domain_count > 0
    msg := sprintf("OneDrive sync is restricted to %d allowed domain(s)", [domain_count])
}

generate_message(restricted, domain_count) := msg if {
    restricted == true
    domain_count == 0
    msg := "OneDrive sync restriction is enabled but no allowed domain GUIDs are configured"
}

generate_message(restricted, _domain_count) := msg if {
    restricted == false
    msg := "OneDrive sync is not restricted for unmanaged devices"
}

generate_affected_resources(true) := []

generate_affected_resources(false) := [
    "OneDrive sync restriction configuration does not meet CIS 7.3.2 requirements"
]