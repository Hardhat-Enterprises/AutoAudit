package cis.microsoft_365_foundations.v6_0_0.test_control_1_1_3

import rego.v1

test_compliant_two_global_admins if {
    result := data.cis.microsoft_365_foundations.v6_0_0.control_1_1_3.result with input as {
        "global_admin_count": 2,
        "global_admins": [
            "admin1@contoso.com",
            "admin2@contoso.com",
        ],
    }

    result.compliant == true
    result.message == "2 global admins configured (within recommended range of 2-4)"
    result.details.global_admin_count == 2
    result.details.recommended_min == 2
    result.details.recommended_max == 4
    count(result.affected_resources) == 2
}

test_compliant_three_global_admins if {
    result := data.cis.microsoft_365_foundations.v6_0_0.control_1_1_3.result with input as {
        "global_admin_count": 3,
        "global_admins": [
            "admin1@contoso.com",
            "admin2@contoso.com",
            "admin3@contoso.com",
        ],
    }

    result.compliant == true
    result.details.global_admin_count == 3
    count(result.affected_resources) == 3
}

test_compliant_four_global_admins if {
    result := data.cis.microsoft_365_foundations.v6_0_0.control_1_1_3.result with input as {
        "global_admin_count": 4,
        "global_admins": [
            "admin1@contoso.com",
            "admin2@contoso.com",
            "admin3@contoso.com",
            "admin4@contoso.com",
        ],
    }

    result.compliant == true
    result.message == "4 global admins configured (within recommended range of 2-4)"
    result.details.global_admin_count == 4
    count(result.affected_resources) == 4
}

test_non_compliant_zero_global_admins if {
    result := data.cis.microsoft_365_foundations.v6_0_0.control_1_1_3.result with input as {
        "global_admin_count": 0,
        "global_admins": [],
    }

    result.compliant == false
    result.message == "Only 0 global admin(s) found. Minimum 2 recommended for continuity."
    result.details.global_admin_count == 0
    count(result.affected_resources) == 0
}

test_non_compliant_one_global_admin if {
    result := data.cis.microsoft_365_foundations.v6_0_0.control_1_1_3.result with input as {
        "global_admin_count": 1,
        "global_admins": [
            "admin1@contoso.com",
        ],
    }

    result.compliant == false
    result.message == "Only 1 global admin(s) found. Minimum 2 recommended for continuity."
    result.details.global_admin_count == 1
    count(result.affected_resources) == 1
}

test_non_compliant_five_global_admins if {
    result := data.cis.microsoft_365_foundations.v6_0_0.control_1_1_3.result with input as {
        "global_admin_count": 5,
        "global_admins": [
            "admin1@contoso.com",
            "admin2@contoso.com",
            "admin3@contoso.com",
            "admin4@contoso.com",
            "admin5@contoso.com",
        ],
    }

    result.compliant == false
    result.message == "5 global admins found. Maximum 4 recommended to minimize attack surface."
    result.details.global_admin_count == 5
    count(result.affected_resources) == 5
}

test_non_compliant_many_global_admins if {
    result := data.cis.microsoft_365_foundations.v6_0_0.control_1_1_3.result with input as {
        "global_admin_count": 10,
        "global_admins": [
            "admin1@contoso.com",
            "admin2@contoso.com",
            "admin3@contoso.com",
            "admin4@contoso.com",
            "admin5@contoso.com",
            "admin6@contoso.com",
            "admin7@contoso.com",
            "admin8@contoso.com",
            "admin9@contoso.com",
            "admin10@contoso.com",
        ],
    }

    result.compliant == false
    result.details.global_admin_count == 10
    result.details.recommended_min == 2
    result.details.recommended_max == 4
}

test_empty_admin_list_with_valid_count if {
    result := data.cis.microsoft_365_foundations.v6_0_0.control_1_1_3.result with input as {
        "global_admin_count": 2,
        "global_admins": [],
    }

    result.compliant == true
    result.details.global_admin_count == 2
    count(result.affected_resources) == 0
}

test_missing_global_admins_uses_empty_array if {
    result := data.cis.microsoft_365_foundations.v6_0_0.control_1_1_3.result with input as {
        "global_admin_count": 3,
    }

    result.compliant == true
    result.details.global_admin_count == 3
    count(result.affected_resources) == 0
}

test_result_structure if {
    result := data.cis.microsoft_365_foundations.v6_0_0.control_1_1_3.result with input as {
        "global_admin_count": 3,
        "global_admins": [
            "admin1@contoso.com",
            "admin2@contoso.com",
            "admin3@contoso.com",
        ],
    }

    _ = result.compliant
    _ = result.message
    _ = result.affected_resources
    _ = result.details.global_admin_count
    _ = result.details.recommended_min
    _ = result.details.recommended_max
}
