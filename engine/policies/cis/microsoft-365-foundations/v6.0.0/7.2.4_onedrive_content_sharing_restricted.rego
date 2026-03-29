# METADATA
# title: Ensure OneDrive content sharing is restricted
# description: |
#   This setting governs the global permissiveness of OneDrive content sharing in the organization.
#   OneDrive content sharing can be restricted independent of SharePoint but can never be more 
#   permissive than the level established with SharePoint.
#   The recommended state is Only people in your organization.
# related_resources:
# - ref: https://www.cisecurity.org/benchmark/microsoft_365
#   description: CIS Microsoft 365 Foundations Benchmark
# custom:
#   control_id: CIS-7.2.4
#   framework: cis
#   benchmark: microsoft-365-foundations
#   version: v6.0.0
#   service: SharePoint
#   requires_permissions:
#   - SharePointTenantSettings.Read.All

package cis.microsoft_365_foundations.v6_0_0.control_7_2_4

default result := {"compliant": false, "message": "Evaluation failed"}

result := {
    "compliant": compliant,
    "message": message,
    "affected_resources": affected_resources,
    "details": {
        "onedrive_sharing_capability": sharing_capability,
    },
} if {
    sharing_capability := object.get(input, "onedrive_sharing_capability", null)
    normalized := lower(sprintf("%v", [sharing_capability]))
    compliant := restricted_value(sharing_capability, normalized)
    message := generate_message(sharing_capability, normalized, compliant)
    affected_resources := generate_affected_resources(sharing_capability, compliant)
}

is_restricted(sharing_capability, normalized) if {
    sharing_capability != null
    not contains(normalized, "anyone")
}

restricted_value(sharing_capability, normalized) := true if {
    is_restricted(sharing_capability, normalized)
} else := false

generate_message(sharing_capability, normalized, compliant) := "OneDrive content sharing is disabled" if {
    sharing_capability != null
    compliant
    normalized == "disabled"
}

generate_message(sharing_capability, normalized, compliant) := "OneDrive content sharing is restricted" if {
    sharing_capability != null
    compliant
    normalized != "disabled"
}

generate_message(sharing_capability, _, compliant) := "OneDrive content sharing allows Anyone links" if {
    sharing_capability != null
    not compliant
}

generate_message(null, _, _) := "Unable to determine the OneDrive sharing capability"

generate_affected_resources(sharing_capability, compliant) := [] if {
    sharing_capability != null
    compliant
}

generate_affected_resources(sharing_capability, compliant) := [sprintf("onedrive_sharing_capability=%v", [sharing_capability])] if {
    sharing_capability != null
    not compliant
}

generate_affected_resources(null, _) := ["OneDrive sharing capability unknown"]
