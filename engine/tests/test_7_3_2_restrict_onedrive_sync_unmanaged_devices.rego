package cis.microsoft_365_foundations.v6_0_0.test_7_3_2

import rego.v1

# ---------------------------------------------------------------------------
# Test: compliant — OneDrive sync is restricted for unmanaged devices
# ---------------------------------------------------------------------------

test_compliant_unmanaged_sync_restricted if {
    result := data.cis.microsoft_365_foundations.v6_0_0.control_7_3_2.result with input as {
        "is_unmanaged_sync_client_for_tenant_restricted": true,
    }

    result.compliant == true
    result.details.is_unmanaged_sync_client_for_tenant_restricted == true
    count(result.affected_resources) == 0
}

# ---------------------------------------------------------------------------
# Test: non-compliant — OneDrive sync is not restricted for unmanaged devices
# ---------------------------------------------------------------------------

test_non_compliant_unmanaged_sync_not_restricted if {
    result := data.cis.microsoft_365_foundations.v6_0_0.control_7_3_2.result with input as {
        "is_unmanaged_sync_client_for_tenant_restricted": false,
    }

    result.compliant == false
    result.details.is_unmanaged_sync_client_for_tenant_restricted == false
    count(result.affected_resources) == 1
}

# ---------------------------------------------------------------------------
# Test: missing evidence must not silently pass
# ---------------------------------------------------------------------------

test_missing_evidence_is_not_compliant if {
    result := data.cis.microsoft_365_foundations.v6_0_0.control_7_3_2.result with input as {}

    result.compliant == false
    result.details.is_unmanaged_sync_client_for_tenant_restricted == null
    result.message == "Unable to determine OneDrive unmanaged-device sync restriction status"
    count(result.affected_resources) == 1
}

# ---------------------------------------------------------------------------
# Test: result contains the expected evidence structure
# ---------------------------------------------------------------------------

test_result_details_structure if {
    result := data.cis.microsoft_365_foundations.v6_0_0.control_7_3_2.result with input as {
        "is_unmanaged_sync_client_for_tenant_restricted": true,
    }

    _ = result.compliant
    _ = result.message
    _ = result.affected_resources
    _ = result.details.is_unmanaged_sync_client_for_tenant_restricted
}
