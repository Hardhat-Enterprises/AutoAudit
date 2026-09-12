# METADATA
# title: Ensure external content sharing is restricted
# description: |
#   Ensures SharePoint external content sharing is restricted
#   to an approved sharing capability.
# related_resources:
# - ref: https://www.cisecurity.org/benchmark/microsoft_365
#   description: CIS Microsoft 365 Foundations Benchmark
# custom:
#   control_id: CIS-7.2.3
#   framework: cis
#   benchmark: microsoft-365-foundations
#   version: v6.0.0
#   severity: medium
#   service: SharePoint
#   requires_permissions:
#   - SharePoint.Admin

package cis.microsoft_365_foundations.v6_0_0.control_7_2_3

default result := {"compliant": false, "message": "Evaluation failed"}

result := output if {
    tenant := object.get(input, "tenant", {})
    sharing_capability := object.get(
        tenant,
        "SharingCapability",
        null
    )

    compliant := sharing_capability in {0, 1, 3}

    output := {
        "compliant": compliant,
        "message": generate_message(sharing_capability),
        "affected_resources": generate_affected_resources(compliant),
        "details": {
            "sharing_capability": sharing_capability
        }
    }
}

generate_message(sharing_capability) := msg if {
    sharing_capability == 0
    msg := "SharePoint external content sharing is disabled"
}

generate_message(sharing_capability) := msg if {
    sharing_capability == 1
    msg := "SharePoint external sharing is limited to authenticated external users"
}

generate_message(sharing_capability) := msg if {
    sharing_capability == 3
    msg := "SharePoint external sharing is limited to existing external users"
}

generate_message(sharing_capability) := msg if {
    sharing_capability == 2
    msg := "SharePoint external content sharing allows external users and guest sharing"
}

generate_message(sharing_capability) := msg if {
    sharing_capability == null
    msg := "Unable to determine SharePoint external sharing capability"
}

generate_message(sharing_capability) := msg if {
    sharing_capability != null
    sharing_capability != 0
    sharing_capability != 1
    sharing_capability != 2
    sharing_capability != 3
    msg := sprintf(
        "Unknown SharePoint sharing capability value: %v",
        [sharing_capability]
    )
}

generate_affected_resources(true) := []
generate_affected_resources(false) := ["SharePoint external content sharing configuration"]
