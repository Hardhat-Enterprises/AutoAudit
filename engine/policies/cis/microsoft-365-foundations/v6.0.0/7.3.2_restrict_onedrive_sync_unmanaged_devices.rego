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
    "message": "Evaluation failed"
}

result := output if {
    restricted := object.get(
        input,
        "is_unmanaged_sync_client_for_tenant_restricted",
        null
    )

    compliant := restricted == true

    output := {
        "compliant": compliant,
        "message": generate_message(restricted),
        "affected_resources": generate_affected_resources(compliant),
        "details": {
            "is_unmanaged_sync_client_for_tenant_restricted": restricted
        }
    }
}

generate_message(restricted) := msg if {
    restricted == true
    msg := "OneDrive sync is restricted for unmanaged devices"
}

generate_message(restricted) := msg if {
    restricted == false
    msg := "OneDrive sync is not restricted for unmanaged devices"
}

generate_message(restricted) := msg if {
    restricted == null
    msg := "Unable to determine OneDrive unmanaged-device sync restriction status"
}

generate_affected_resources(true) := []

generate_affected_resources(false) := [
    "OneDrive sync is permitted from unmanaged devices"
]
