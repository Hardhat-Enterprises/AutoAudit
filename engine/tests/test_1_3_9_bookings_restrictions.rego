package cis.microsoft_365_foundations.v6_0_0.test_control_1_3_9

import rego.v1


# ---------------------------------------------------------------------------
# Test: compliant — Default OWA policy has bookings disabled
# ---------------------------------------------------------------------------

test_compliant_owa_policy_disabled if {
    result := data.cis.microsoft_365_foundations.v6_0_0.control_1_3_9.result with input as {
        "owa_mailbox_policy": {
            "default_policy_bookings_mailbox_creation_enabled": false,
            "bookings_enabled": true,
        }
    }

    result.compliant == true
    contains(result.message, "appropriately restricted")
    result.details.default_policy_bookings_mailbox_creation_enabled == false
    result.details.bookings_enabled == true
}


# ---------------------------------------------------------------------------
# Test: compliant — Organization-level bookings disabled
# ---------------------------------------------------------------------------

test_compliant_org_level_disabled if {
    result := data.cis.microsoft_365_foundations.v6_0_0.control_1_3_9.result with input as {
        "owa_mailbox_policy": {
            "default_policy_bookings_mailbox_creation_enabled": true,
            "bookings_enabled": false,
        }
    }

    result.compliant == true
    contains(result.message, "appropriately restricted")
    result.details.bookings_enabled == false
}


# ---------------------------------------------------------------------------
# Test: compliant — Both disabled (most restrictive)
# ---------------------------------------------------------------------------

test_compliant_both_disabled if {
    result := data.cis.microsoft_365_foundations.v6_0_0.control_1_3_9.result with input as {
        "owa_mailbox_policy": {
            "default_policy_bookings_mailbox_creation_enabled": false,
            "bookings_enabled": false,
        }
    }

    result.compliant == true
    contains(result.message, "appropriately restricted")
}


# ---------------------------------------------------------------------------
# Test: non-compliant — Both enabled (least restrictive)
# ---------------------------------------------------------------------------

test_non_compliant_both_enabled if {
    result := data.cis.microsoft_365_foundations.v6_0_0.control_1_3_9.result with input as {
        "owa_mailbox_policy": {
            "default_policy_bookings_mailbox_creation_enabled": true,
            "bookings_enabled": true,
        }
    }

    result.compliant == false
    contains(result.message, "enabled and not restricted")
    result.details.default_policy_bookings_mailbox_creation_enabled == true
    result.details.bookings_enabled == true
}


# ---------------------------------------------------------------------------
# Test: non-compliant — Missing evidence (null values)
# ---------------------------------------------------------------------------

test_non_compliant_missing_evidence if {
    result := data.cis.microsoft_365_foundations.v6_0_0.control_1_3_9.result with input as {
        "owa_mailbox_policy": {
            "default_policy_bookings_mailbox_creation_enabled": null,
            "bookings_enabled": null,
        }
    }

    result.compliant == false
}


# ---------------------------------------------------------------------------
# Test: result contains expected evidence fields
# ---------------------------------------------------------------------------

test_result_details_structure if {
    result := data.cis.microsoft_365_foundations.v6_0_0.control_1_3_9.result with input as {
        "owa_mailbox_policy": {
            "default_policy_bookings_mailbox_creation_enabled": false,
            "bookings_enabled": true,
        }
    }

    _ := result.details.default_policy_bookings_mailbox_creation_enabled
    _ := result.details.bookings_enabled
    _ := result.compliant
    _ := result.message
}