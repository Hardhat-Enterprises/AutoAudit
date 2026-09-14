package cis.microsoft_365_foundations.v6_0_0.test_7_3_2

import rego.v1

# ------------------------------------------------------------------
# Test: compliant - restriction enabled and domains configured
# ------------------------------------------------------------------

test_compliant_restricted_with_domains if {
    result := data.cis.microsoft_365_foundations.v6_0_0.control_7_3_2.result with input as {
        "is_unmanaged_sync_client_for_tenant_restricted": true,
        "allowed_domain_list": [
            "786548dd-877b-4760-a749-6b1efbc1190a",
            "877564ff-877b-4760-a749-6b1efbc1190a",
        ],
    }

    result.compliant == true
    result.message == "OneDrive sync is restricted to 2 allowed domain(s)"
    result.details.is_unmanaged_sync_client_for_tenant_restricted == true
    result.details.allowed_domain_count == 2
    count(result.affected_resources) == 0
}

# ------------------------------------------------------------------
# Test: non-compliant - restriction disabled
# ------------------------------------------------------------------

test_non_compliant_restriction_disabled if {
    result := data.cis.microsoft_365_foundations.v6_0_0.control_7_3_2.result with input as {
        "is_unmanaged_sync_client_for_tenant_restricted": false,
        "allowed_domain_list": [],
    }

    result.compliant == false
    result.message == "OneDrive sync is not restricted for unmanaged devices"
    result.details.is_unmanaged_sync_client_for_tenant_restricted == false
    count(result.affected_resources) == 1
}

# ------------------------------------------------------------------
# Test: restriction enabled but no allowed domains configured
# ------------------------------------------------------------------

test_non_compliant_enabled_but_no_domains_configured if {
    result := data.cis.microsoft_365_foundations.v6_0_0.control_7_3_2.result with input as {
        "is_unmanaged_sync_client_for_tenant_restricted": true,
        "allowed_domain_list": [],
    }

    result.compliant == false
    result.message == "OneDrive sync restriction is enabled but no allowed domain GUIDs are configured"
    result.details.allowed_domain_count == 0
    count(result.affected_resources) == 1
}

# ------------------------------------------------------------------
# Test: missing restriction evidence must fail closed
# ------------------------------------------------------------------

test_non_compliant_missing_restriction_evidence if {
    result := data.cis.microsoft_365_foundations.v6_0_0.control_7_3_2.result with input as {
        "allowed_domain_list": [
            "786548dd-877b-4760-a749-6b1efbc1190a",
        ],
    }

    result.compliant == false
    result.message == "Evaluation failed: unable to determine OneDrive sync client restriction status"
    result.details == {}
    count(result.affected_resources) == 0
}

# ------------------------------------------------------------------
# Test: missing allowed_domain_list behaves like empty list
# ------------------------------------------------------------------

test_non_compliant_missing_allowed_domain_list if {
    result := data.cis.microsoft_365_foundations.v6_0_0.control_7_3_2.result with input as {
        "is_unmanaged_sync_client_for_tenant_restricted": true,
    }

    result.compliant == false
    result.message == "OneDrive sync restriction is enabled but no allowed domain GUIDs are configured"
    result.details.allowed_domain_count == 0
    result.details.allowed_domain_list == []
    count(result.affected_resources) == 1
}

# ------------------------------------------------------------------
# Test: result contains expected evidence structure
# ------------------------------------------------------------------

test_result_details_structure if {
    result := data.cis.microsoft_365_foundations.v6_0_0.control_7_3_2.result with input as {
        "is_unmanaged_sync_client_for_tenant_restricted": true,
        "allowed_domain_list": [
            "786548dd-877b-4760-a749-6b1efbc1190a",
        ],
    }

    _ = result.compliant
    _ = result.message
    _ = result.affected_resources
    _ = result.details.is_unmanaged_sync_client_for_tenant_restricted
    _ = result.details.allowed_domain_list
    _ = result.details.allowed_domain_count
}