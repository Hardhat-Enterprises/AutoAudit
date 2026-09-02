package cis.microsoft_365_foundations.v6_0_0.test_control_1_2_2

import rego.v1

test_compliant_no_shared_mailboxes if {
    result := data.cis.microsoft_365_foundations.v6_0_0.control_1_2_2.result with input as {
        "shared_mailboxes": [],
        "total_shared_mailboxes": 0,
    }

    result.compliant == true
    result.message == "No shared mailboxes found."
    result.details.total_shared_mailboxes == 0
    result.details.direct_sign_in_enabled_count == 0
}

test_compliant_all_shared_mailboxes_blocked if {
    result := data.cis.microsoft_365_foundations.v6_0_0.control_1_2_2.result with input as {
        "shared_mailboxes": [
            {
                "display_name": "Support Shared Mailbox",
                "user_principal_name": "support@contoso.com",
                "external_directory_object_id": "11111111-1111-1111-1111-111111111111",
                "account_disabled": true,
            },
            {
                "display_name": "Finance Shared Mailbox",
                "user_principal_name": "finance@contoso.com",
                "external_directory_object_id": "22222222-2222-2222-2222-222222222222",
                "account_disabled": true,
            },
        ],
        "total_shared_mailboxes": 2,
    }

    result.compliant == true
    result.message == "Sign-in is blocked for all 2 shared mailbox(es)."
    result.details.total_shared_mailboxes == 2
    result.details.blocked_sign_in_count == 2
    result.details.direct_sign_in_enabled_count == 0
    count(result.affected_resources) == 0
}

test_non_compliant_one_shared_mailbox_enabled if {
    result := data.cis.microsoft_365_foundations.v6_0_0.control_1_2_2.result with input as {
        "shared_mailboxes": [
            {
                "display_name": "Support Shared Mailbox",
                "user_principal_name": "support@contoso.com",
                "external_directory_object_id": "11111111-1111-1111-1111-111111111111",
                "account_disabled": true,
            },
            {
                "display_name": "Finance Shared Mailbox",
                "user_principal_name": "finance@contoso.com",
                "external_directory_object_id": "22222222-2222-2222-2222-222222222222",
                "account_disabled": false,
            },
        ],
        "total_shared_mailboxes": 2,
    }

    result.compliant == false
    result.message == "1 of 2 shared mailbox(es) allow direct sign-in."
    result.details.total_shared_mailboxes == 2
    result.details.blocked_sign_in_count == 1
    result.details.direct_sign_in_enabled_count == 1
    count(result.affected_resources) == 1
    result.affected_resources[0].user_principal_name == "finance@contoso.com"
}

test_non_compliant_all_shared_mailboxes_enabled if {
    result := data.cis.microsoft_365_foundations.v6_0_0.control_1_2_2.result with input as {
        "shared_mailboxes": [
            {
                "display_name": "Support Shared Mailbox",
                "user_principal_name": "support@contoso.com",
                "external_directory_object_id": "11111111-1111-1111-1111-111111111111",
                "account_disabled": false,
            },
            {
                "display_name": "Finance Shared Mailbox",
                "user_principal_name": "finance@contoso.com",
                "external_directory_object_id": "22222222-2222-2222-2222-222222222222",
                "account_disabled": false,
            },
        ],
        "total_shared_mailboxes": 2,
    }

    result.compliant == false
    result.message == "2 of 2 shared mailbox(es) allow direct sign-in."
    result.details.blocked_sign_in_count == 0
    result.details.direct_sign_in_enabled_count == 2
    count(result.affected_resources) == 2
}

test_non_compliant_unknown_status_null if {
    result := data.cis.microsoft_365_foundations.v6_0_0.control_1_2_2.result with input as {
        "shared_mailboxes": [
            {
                "display_name": "Support Shared Mailbox",
                "user_principal_name": "support@contoso.com",
                "external_directory_object_id": "33333333-3333-3333-3333-333333333333",
                "account_disabled": null,
            },
        ],
        "total_shared_mailboxes": 1,
    }

    result.compliant == false
    result.message == "Unable to determine sign-in status for 1 shared mailbox(es)."
    result.details.total_shared_mailboxes == 1
    result.details.unknown_status_count == 1
    count(result.affected_resources) == 1
}

test_non_compliant_missing_account_disabled if {
    result := data.cis.microsoft_365_foundations.v6_0_0.control_1_2_2.result with input as {
        "shared_mailboxes": [
            {
                "display_name": "Support Shared Mailbox",
                "user_principal_name": "support@contoso.com",
                "external_directory_object_id": "33333333-3333-3333-3333-333333333333",
            },
        ],
        "total_shared_mailboxes": 1,
    }

    result.compliant == false
    result.message == "Unable to determine sign-in status for 1 shared mailbox(es)."
    result.details.unknown_status_count == 1
}

test_mixed_enabled_and_unknown_status_prefers_unknown_evaluation if {
    result := data.cis.microsoft_365_foundations.v6_0_0.control_1_2_2.result with input as {
        "shared_mailboxes": [
            {
                "display_name": "Finance Shared Mailbox",
                "user_principal_name": "finance@contoso.com",
                "external_directory_object_id": "22222222-2222-2222-2222-222222222222",
                "account_disabled": false,
            },
            {
                "display_name": "Support Shared Mailbox",
                "user_principal_name": "support@contoso.com",
                "external_directory_object_id": "33333333-3333-3333-3333-333333333333",
                "account_disabled": null,
            },
        ],
        "total_shared_mailboxes": 2,
    }

    result.compliant == false
    result.message == "Unable to determine sign-in status for 1 shared mailbox(es)."
    result.details.unknown_status_count == 1
}

test_result_structure if {
    result := data.cis.microsoft_365_foundations.v6_0_0.control_1_2_2.result with input as {
        "shared_mailboxes": [
            {
                "display_name": "Support Shared Mailbox",
                "user_principal_name": "support@contoso.com",
                "external_directory_object_id": "11111111-1111-1111-1111-111111111111",
                "account_disabled": true,
            },
        ],
        "total_shared_mailboxes": 1,
    }

    _ = result.compliant
    _ = result.message
    _ = result.affected_resources
    _ = result.details.total_shared_mailboxes
    _ = result.details.blocked_sign_in_count
    _ = result.details.direct_sign_in_enabled_count
}