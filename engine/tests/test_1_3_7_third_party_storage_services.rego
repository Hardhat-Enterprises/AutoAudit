package cis.microsoft_365_foundations.v6_0_0.test_1_3_7

import rego.v1

# ---------------------------------------------------------------------------
# Test: compliant — service principal exists and is disabled
# ---------------------------------------------------------------------------

test_compliant_service_principal_disabled if {
    result := data.cis.microsoft_365_foundations.v6_0_0.control_1_3_7.result with input as {
        "service_principal_exists": true,
        "account_enabled": false,
        "service_principal": {
            "id": "sp-001",
            "appId": "c1f33bc0-bdb4-4248-ba9b-096807ddb43e",
            "accountEnabled": false,
        },
        "collector_error": null,
    }
    result.compliant == true
    result.details.service_principal_exists == true
    result.details.account_enabled == false
    count(result.affected_resources) == 0
}

# ---------------------------------------------------------------------------
# Test: non-compliant — service principal has never been created (default state)
# ---------------------------------------------------------------------------

test_non_compliant_service_principal_not_created if {
    result := data.cis.microsoft_365_foundations.v6_0_0.control_1_3_7.result with input as {
        "service_principal_exists": false,
        "account_enabled": null,
        "service_principal": null,
        "collector_error": null,
    }
    result.compliant == false
    result.details.service_principal_exists == false
    count(result.affected_resources) == 1
}

# ---------------------------------------------------------------------------
# Test: non-compliant — service principal exists but is still enabled
# ---------------------------------------------------------------------------

test_non_compliant_service_principal_enabled if {
    result := data.cis.microsoft_365_foundations.v6_0_0.control_1_3_7.result with input as {
        "service_principal_exists": true,
        "account_enabled": true,
        "service_principal": {
            "id": "sp-001",
            "appId": "c1f33bc0-bdb4-4248-ba9b-096807ddb43e",
            "accountEnabled": true,
        },
        "collector_error": null,
    }
    result.compliant == false
    result.details.account_enabled == true
    count(result.affected_resources) == 1
}

# ---------------------------------------------------------------------------
# Test: details include correct evidence fields
# ---------------------------------------------------------------------------

test_result_details_structure if {
    result := data.cis.microsoft_365_foundations.v6_0_0.control_1_3_7.result with input as {
        "service_principal_exists": true,
        "account_enabled": false,
        "service_principal": {
            "id": "sp-001",
            "appId": "c1f33bc0-bdb4-4248-ba9b-096807ddb43e",
            "accountEnabled": false,
        },
        "collector_error": null,
    }
    _ = result.compliant
    _ = result.message
    _ = result.affected_resources
    _ = result.details.service_principal_exists
    _ = result.details.account_enabled
    _ = result.details.app_id
}