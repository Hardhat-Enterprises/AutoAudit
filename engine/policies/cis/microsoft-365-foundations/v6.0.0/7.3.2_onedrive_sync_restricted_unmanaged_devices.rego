# METADATA
# title: Ensure OneDrive sync is restricted for unmanaged devices
# description: |
#   OneDrive sync should be restricted to computers joined to specific,
#   trusted Active Directory domains so unmanaged devices cannot sync
#   organizational data outside the organization's control.
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
    enabled := input.tenant_restriction_enabled
    enabled != null

    domains := object.get(input, "allowed_domain_list", [])
    domain_count := count(domains)

    is_compliant := is_restricted(enabled, domain_count)

    output := {
        "compliant": is_compliant,
        "message": generate_message(enabled, domain_count),
        "affected_resources": generate_affected_resources(is_compliant),
        "details": {
            "tenant_restriction_enabled": enabled,
            "allowed_domain_list": domains,
            "allowed_domain_count": domain_count
        }
    }
}

# Compliant only when sync is restricted to specific domains AND at least one
# trusted domain GUID has been configured. CIS 7.3.2 also requires the
# configured GUIDs to be the organization's actual trusted on-prem domains --
# that cannot be verified automatically from this data alone, so this checks
# only that the restriction is on and at least one domain has been
# configured (see metadata.json notes for this control).
is_restricted(enabled, domain_count) := true if {
    enabled == true
    domain_count > 0
} else := false

generate_message(enabled, domain_count) := msg if {
    enabled == true
    domain_count > 0
    msg := sprintf("OneDrive sync is restricted to %d allowed domain(s)", [domain_count])
}

generate_message(enabled, domain_count) := msg if {
    enabled == true
    domain_count == 0
    msg := "OneDrive sync restriction is enabled but no allowed domain GUIDs are configured"
}

generate_message(enabled, _) := msg if {
    enabled == false
    msg := "OneDrive sync is not restricted to specific domains (TenantRestrictionEnabled is False)"
}

generate_affected_resources(true) := []

generate_affected_resources(false) := [
    "OneDrive sync client restriction (TenantRestrictionEnabled/AllowedDomainList)"
]
