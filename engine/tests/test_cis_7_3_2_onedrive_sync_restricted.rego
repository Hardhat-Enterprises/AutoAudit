package cis.microsoft_365_foundations.v6_0_0.test_control_7_3_2

import rego.v1

# ---------------------------------------------------------------------------
# Test: compliant -- restriction enabled and domains configured
# ---------------------------------------------------------------------------

test_compliant_restricted_with_domains if {
    result := data.cis.microsoft_365_foundations.v6_0_0.control_7_3_2.result with input as {
        "tenant_restriction_enabled": true,
        "allowed_domain_list": [
            "786548dd-877b-4760-a749-6b1efbc1190a",
            "877564ff-877b-4760-a749-6b1efbc1190a",
        ],
    }
    result.compliant == true
    result.message == "OneDrive sync is restricted to 2 allowed domain(s)"
    result.details.tenant_restriction_enabled == true
    result.details.allowed_domain_count == 2
    count(result.affected_resources) == 0
}

# ---------------------------------------------------------------------------
# Test: non-compliant -- restriction disabled (CIS default tenant state)
# ---------------------------------------------------------------------------

test_non_compliant_restriction_disabled if {
    result := data.cis.microsoft_365_foundations.v6_0_0.control_7_3_2.result with input as {
        "tenant_restriction_enabled": false,
        "allowed_domain_list": [],
    }
    result.compliant == false
    result.message == "OneDrive sync is not restricted to specific domains (TenantRestrictionEnabled is False)"
    result.details.tenant_restriction_enabled == false
    count(result.affected_resources) == 1
}

# ---------------------------------------------------------------------------
# Test (edge case specific to 7.3.2): restriction enabled but no domain GUIDs
# configured -- CIS audits both TenantRestrictionEnabled AND AllowedDomainList,
# so "enabled" alone must not be treated as compliant.
# ---------------------------------------------------------------------------

test_non_compliant_enabled_but_no_domains_configured if {
    result := data.cis.microsoft_365_foundations.v6_0_0.control_7_3_2.result with input as {
        "tenant_restriction_enabled": true,
        "allowed_domain_list": [],
    }
    result.compliant == false
    result.message == "OneDrive sync restriction is enabled but no allowed domain GUIDs are configured"
    result.details.allowed_domain_count == 0
    count(result.affected_resources) == 1
}

# ---------------------------------------------------------------------------
# Test: missing data -- tenant_restriction_enabled absent from input entirely
# (collector failure / unexpected shape) falls back to the fail-closed default
# ---------------------------------------------------------------------------

test_non_compliant_missing_tenant_restriction_enabled if {
    result := data.cis.microsoft_365_foundations.v6_0_0.control_7_3_2.result with input as {
        "allowed_domain_list": ["786548dd-877b-4760-a749-6b1efbc1190a"],
    }
    result.compliant == false
    result.message == "Evaluation failed: unable to determine OneDrive sync client restriction status"
    result.details == {}
}

# ---------------------------------------------------------------------------
# Test: empty data -- allowed_domain_list key missing entirely (not just an
# empty list) must be treated the same as an empty list, not as missing data
# ---------------------------------------------------------------------------

test_non_compliant_missing_allowed_domain_list_key if {
    result := data.cis.microsoft_365_foundations.v6_0_0.control_7_3_2.result with input as {
        "tenant_restriction_enabled": true,
    }
    result.compliant == false
    result.details.allowed_domain_count == 0
    result.details.allowed_domain_list == []
}

# ---------------------------------------------------------------------------
# Test: result structure -- required fields are present
# ---------------------------------------------------------------------------

test_result_structure if {
    result := data.cis.microsoft_365_foundations.v6_0_0.control_7_3_2.result with input as {
        "tenant_restriction_enabled": true,
        "allowed_domain_list": ["786548dd-877b-4760-a749-6b1efbc1190a"],
    }
    _ = result.compliant
    _ = result.message
    _ = result.affected_resources
    _ = result.details.tenant_restriction_enabled
    _ = result.details.allowed_domain_list
    _ = result.details.allowed_domain_count
}
