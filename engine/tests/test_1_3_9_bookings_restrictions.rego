package cis.microsoft_365_foundations.v6_0_0.test_control_1_3_9

import rego.v1

test_compliant_bookings_disabled_by_default if {
    result := data.cis.microsoft_365_foundations.v6_0_0.control_1_3_9.result with input as {
        "default_policy_bookings_mailbox_creation_enabled": false,
        "bookings_enabled": true,
        "policies_with_bookings": [],
        "total_policies": 1,
    }
    result.compliant == true
    contains(result.message, "restricted")
}

# --- New: compliant via the tenant-wide switch alone (the case Codex flagged) ---

test_compliant_via_tenant_wide_bookings_disabled if {
    result := data.cis.microsoft_365_foundations.v6_0_0.control_1_3_9.result with input as {
        "default_policy_bookings_mailbox_creation_enabled": true,
        "bookings_enabled": false,
        "policies_with_bookings": ["Default"],
        "total_policies": 1,
    }
    result.compliant == true
    contains(result.message, "restricted")
}

test_non_compliant_bookings_enabled_by_default if {
    result := data.cis.microsoft_365_foundations.v6_0_0.control_1_3_9.result with input as {
        "default_policy_bookings_mailbox_creation_enabled": true,
        "bookings_enabled": true,
        "policies_with_bookings": ["Default"],
        "total_policies": 1,
    }
    result.compliant == false
    contains(result.message, "not restricted")
}

test_unable_to_determine_when_null if {
    result := data.cis.microsoft_365_foundations.v6_0_0.control_1_3_9.result with input as {
        "default_policy_bookings_mailbox_creation_enabled": null,
        "bookings_enabled": false,
        "policies_with_bookings": [],
        "total_policies": 1,
    }
    result.compliant == false
    result.message == "Unable to determine Bookings configuration"
}

test_unable_to_determine_when_missing if {
    result := data.cis.microsoft_365_foundations.v6_0_0.control_1_3_9.result with input as {}
    result.compliant == false
    result.message == "Unable to determine Bookings configuration"
}