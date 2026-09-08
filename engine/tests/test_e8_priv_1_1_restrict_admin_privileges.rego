package essential_eight.asd_essential_eight.v2025.test_e8_priv_1_1

import rego.v1

test_compliant_cloud_only_within_threshold if {
    result := data.essential_eight.asd_essential_eight.v2025.control_e8_priv_1_1.result with input as {
        "admin_accounts": [
            {"id": "u1", "userPrincipalName": "admin1@contoso.com", "displayName": "Admin One", "on_premises_sync_enabled": false, "admin_roles": ["Global Administrator"]},
            {"id": "u2", "userPrincipalName": "admin2@contoso.com", "displayName": "Admin Two", "on_premises_sync_enabled": false, "admin_roles": ["Security Administrator"]},
        ],
        "total_admin_accounts": 2,
        "cloud_only_admin_count": 2,
        "synced_admin_count": 0,
    }
    result.compliant == true
    result.details.synced_admin_count == 0
    result.details.threshold_exceeded == false
}

test_non_compliant_zero_admin_accounts if {
    result := data.essential_eight.asd_essential_eight.v2025.control_e8_priv_1_1.result with input as {
        "admin_accounts": [],
        "total_admin_accounts": 0,
        "cloud_only_admin_count": 0,
        "synced_admin_count": 0,
    }
    result.compliant == false
    result.message == "No admin accounts detected - check collector permissions"
}

test_non_compliant_synced_account if {
    result := data.essential_eight.asd_essential_eight.v2025.control_e8_priv_1_1.result with input as {
        "admin_accounts": [
            {"id": "u1", "userPrincipalName": "admin1@contoso.com", "displayName": "Admin One", "on_premises_sync_enabled": false, "admin_roles": ["Global Administrator"]},
            {"id": "u2", "userPrincipalName": "synced@contoso.com", "displayName": "Synced Admin", "on_premises_sync_enabled": true, "admin_roles": ["Exchange Administrator"]},
        ],
        "total_admin_accounts": 2,
        "cloud_only_admin_count": 1,
        "synced_admin_count": 1,
    }
    result.compliant == false
    result.details.synced_admin_count == 1
    "synced@contoso.com" in result.details.synced_accounts
}

test_non_compliant_threshold_exceeded if {
    result := data.essential_eight.asd_essential_eight.v2025.control_e8_priv_1_1.result with input as {
        "admin_accounts": [
            {"id": "u1", "userPrincipalName": "a1@contoso.com", "displayName": "Admin 1", "on_premises_sync_enabled": false, "admin_roles": ["Global Administrator"]},
            {"id": "u2", "userPrincipalName": "a2@contoso.com", "displayName": "Admin 2", "on_premises_sync_enabled": false, "admin_roles": ["Security Administrator"]},
            {"id": "u3", "userPrincipalName": "a3@contoso.com", "displayName": "Admin 3", "on_premises_sync_enabled": false, "admin_roles": ["Exchange Administrator"]},
            {"id": "u4", "userPrincipalName": "a4@contoso.com", "displayName": "Admin 4", "on_premises_sync_enabled": false, "admin_roles": ["SharePoint Administrator"]},
            {"id": "u5", "userPrincipalName": "a5@contoso.com", "displayName": "Admin 5", "on_premises_sync_enabled": false, "admin_roles": ["User Administrator"]},
            {"id": "u6", "userPrincipalName": "a6@contoso.com", "displayName": "Admin 6", "on_premises_sync_enabled": false, "admin_roles": ["Compliance Administrator"]},
        ],
        "total_admin_accounts": 6,
        "cloud_only_admin_count": 6,
        "synced_admin_count": 0,
    }
    result.compliant == false
    result.details.threshold_exceeded == true
}

test_compliant_at_threshold if {
    result := data.essential_eight.asd_essential_eight.v2025.control_e8_priv_1_1.result with input as {
        "admin_accounts": [
            {"id": "u1", "userPrincipalName": "a1@contoso.com", "displayName": "Admin 1", "on_premises_sync_enabled": false, "admin_roles": ["Global Administrator"]},
            {"id": "u2", "userPrincipalName": "a2@contoso.com", "displayName": "Admin 2", "on_premises_sync_enabled": false, "admin_roles": ["Security Administrator"]},
            {"id": "u3", "userPrincipalName": "a3@contoso.com", "displayName": "Admin 3", "on_premises_sync_enabled": false, "admin_roles": ["Exchange Administrator"]},
            {"id": "u4", "userPrincipalName": "a4@contoso.com", "displayName": "Admin 4", "on_premises_sync_enabled": false, "admin_roles": ["SharePoint Administrator"]},
            {"id": "u5", "userPrincipalName": "a5@contoso.com", "displayName": "Admin 5", "on_premises_sync_enabled": false, "admin_roles": ["User Administrator"]},
        ],
        "total_admin_accounts": 5,
        "cloud_only_admin_count": 5,
        "synced_admin_count": 0,
    }
    result.compliant == true
    result.details.threshold_exceeded == false
}

test_result_details_structure if {
    result := data.essential_eight.asd_essential_eight.v2025.control_e8_priv_1_1.result with input as {
        "admin_accounts": [
            {"id": "u1", "userPrincipalName": "admin@contoso.com", "displayName": "Admin", "on_premises_sync_enabled": false, "admin_roles": ["Global Administrator"]},
        ],
        "total_admin_accounts": 1,
        "cloud_only_admin_count": 1,
        "synced_admin_count": 0,
    }
    _ = result.compliant
    _ = result.message
    _ = result.details.total_admin_accounts
    _ = result.details.cloud_only_admin_count
    _ = result.details.synced_admin_count
    _ = result.details.synced_accounts
    _ = result.details.threshold
    _ = result.details.threshold_exceeded
}
