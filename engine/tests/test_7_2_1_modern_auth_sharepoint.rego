package cis.microsoft_365_foundations.v6_0_0.test_7_2_1

import rego.v1

# ---------------------------------------------------------------------------
# Test: compliant — legacy auth protocols disabled
# ---------------------------------------------------------------------------

test_compliant_legacy_auth_disabled if {
    result := data.cis.microsoft_365_foundations.v6_0_0.control_7_2_1.result with input as {
        "legacy_auth_protocols_enabled": false,
    }
    result.compliant == true
    result.details.legacy_auth_protocols_enabled == false
    count(result.affected_resources) == 0
}

# ---------------------------------------------------------------------------
# Test: non-compliant — legacy auth protocols enabled
# ---------------------------------------------------------------------------

test_non_compliant_legacy_auth_enabled if {
    result := data.cis.microsoft_365_foundations.v6_0_0.control_7_2_1.result with input as {
        "legacy_auth_protocols_enabled": true,
    }
    result.compliant == false
    result.details.legacy_auth_protocols_enabled == true
    count(result.affected_resources) == 1
}

# ---------------------------------------------------------------------------
# Test: non-compliant — evidence missing/null (must not silently pass)
# ---------------------------------------------------------------------------

test_non_compliant_missing_evidence if {
    result := data.cis.microsoft_365_foundations.v6_0_0.control_7_2_1.result with input as {
        "legacy_auth_protocols_enabled": null,
    }
    result.compliant == false
    result.details.legacy_auth_protocols_enabled == null
    count(result.affected_resources) == 1
}

# ---------------------------------------------------------------------------
# Test: result structure contains all expected fields
# ---------------------------------------------------------------------------

test_result_details_structure if {
    result := data.cis.microsoft_365_foundations.v6_0_0.control_7_2_1.result with input as {
        "legacy_auth_protocols_enabled": false,
    }
    _ = result.compliant
    _ = result.message
    _ = result.affected_resources
    _ = result.details.legacy_auth_protocols_enabled
}