# METADATA
# title: Ensure external content sharing is restricted
# description: |
#   The external sharing settings govern sharing for the organization overall. 
#   Each site has its own sharing setting that can be set independently, 
#   though it must be at the same or more restrictive setting as the organization.
#   The recommended state is New and existing guests or less permissive.
# related_resources:
# - ref: https://www.cisecurity.org/benchmark/microsoft_365
#   description: CIS Microsoft 365 Foundations Benchmark
# custom:
#   control_id: CIS-7.2.3
#   framework: cis
#   benchmark: microsoft-365-foundations
#   version: v6.0.0
#   service: SharePoint
#   requires_permissions:
#   - SharePointTenantSettings.Read.All

package cis.microsoft_365_foundations.v6_0_0.control_7_2_3

default result := {"compliant": false, "message": "Evaluation failed"}

result := {
    "compliant": compliant,
    "message": message,
    "affected_resources": affected_resources,
    "details": {
        "sharing_capability": sharing_capability,
    },
} if {
    sharing_capability := object.get(input, "sharing_capability", null)
    normalized := lower(sprintf("%v", [sharing_capability]))
    compliant := is_restricted(sharing_capability, normalized)
    message := generate_message(sharing_capability, normalized, compliant)
    affected_resources := generate_affected_resources(sharing_capability, compliant)
}

is_restricted(sharing_capability, normalized) if {
    sharing_capability != null
    not contains(normalized, "anyone")
}

generate_message(sharing_capability, normalized, compliant) := "SharePoint external content sharing is disabled" if {
    sharing_capability != null
    compliant
    normalized == "disabled"
}

generate_message(sharing_capability, normalized, compliant) := "SharePoint external content sharing is restricted" if {
    sharing_capability != null
    compliant
    normalized != "disabled"
}

generate_message(sharing_capability, _, compliant) := "SharePoint external content sharing allows Anyone links" if {
    sharing_capability != null
    not compliant
}

generate_message(null, _, _) := "Unable to determine the SharePoint external sharing capability"

generate_affected_resources(sharing_capability, compliant) := [] if {
    sharing_capability != null
    compliant
}

generate_affected_resources(sharing_capability, compliant) := [sprintf("sharing_capability=%v", [sharing_capability])] if {
    sharing_capability != null
    not compliant
}

generate_affected_resources(null, _) := ["SharePoint external sharing capability unknown"]
