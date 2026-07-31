package cis.microsoft_365_foundations.v6_0_0.test_control_5_1_4_4

import rego.v1


# ---------------------------------------------------------------------------
# Test: compliant — Selected users/groups configured
# ---------------------------------------------------------------------------

test_compliant_selected_users if {

    result := data.cis.microsoft_365_foundations.v6_0_0.control_5_1_4_4.result with input as {

        "local_admin_registering_users_type":
            "#microsoft.graph.enumeratedDeviceRegistrationMembership",

        "enable_global_admins": true
    }

    result.compliant == true
    contains(result.message, "limited")

    result.details.local_admin_registering_users_type ==
        "#microsoft.graph.enumeratedDeviceRegistrationMembership"
}


# ---------------------------------------------------------------------------
# Test: compliant — No registering users added as local administrators
# ---------------------------------------------------------------------------

test_compliant_no_registering_users if {

    result := data.cis.microsoft_365_foundations.v6_0_0.control_5_1_4_4.result with input as {

        "local_admin_registering_users_type":
            "#microsoft.graph.noDeviceRegistrationMembership",

        "enable_global_admins": true
    }

    result.compliant == true
    contains(result.message, "limited")

}


# ---------------------------------------------------------------------------
# Test: non-compliant — All users become local administrators
# ---------------------------------------------------------------------------

test_non_compliant_all_users if {

    result := data.cis.microsoft_365_foundations.v6_0_0.control_5_1_4_4.result with input as {

        "local_admin_registering_users_type":
            "#microsoft.graph.allDeviceRegistrationMembership",

        "enable_global_admins": true
    }

    result.compliant == false

    contains(
        result.message,
        "All users registering Entra joined devices are assigned local administrator rights"
    )

    result.details.local_admin_registering_users_type ==
        "#microsoft.graph.allDeviceRegistrationMembership"
}


# ---------------------------------------------------------------------------
# Test: non-compliant — Missing evidence
# ---------------------------------------------------------------------------

test_non_compliant_missing_configuration if {

    result := data.cis.microsoft_365_foundations.v6_0_0.control_5_1_4_4.result with input as {

        "enable_global_admins": true
    }

    result.compliant == false

}


# ---------------------------------------------------------------------------
# Test: result contains expected evidence fields
# ---------------------------------------------------------------------------

test_result_details_structure if {

    result := data.cis.microsoft_365_foundations.v6_0_0.control_5_1_4_4.result with input as {

        "local_admin_registering_users_type":
            "#microsoft.graph.enumeratedDeviceRegistrationMembership",

        "enable_global_admins": true
    }


    _ = result.details.local_admin_registering_users_type
    _ = result.details.global_admins_enabled
}