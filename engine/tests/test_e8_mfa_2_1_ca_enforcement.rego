package essential_eight.asd_essential_eight.v2025.test_e8_mfa_2_1

import rego.v1

# ---------------------------------------------------------------------------
# Helpers: build minimal policy summaries matching what the collector emits
# ---------------------------------------------------------------------------

_mfa_all_users_all_apps := {
    "id": "policy-001",
    "display_name": "Require MFA for all users",
    "state": "enabled",
    "targets_all_users": true,
    "targets_all_apps": true,
    "include_roles": [],
    "include_roles_count": 0,
    "exclude_users": [],
    "exclude_groups": [],
    "has_exclusions": false,
    "requires_mfa": true,
}

_mfa_all_users_all_apps_with_exclusions := {
    "id": "policy-002",
    "display_name": "Require MFA - with exclusions",
    "state": "enabled",
    "targets_all_users": true,
    "targets_all_apps": true,
    "include_roles": [],
    "include_roles_count": 0,
    "exclude_users": ["breakglass@contoso.com"],
    "exclude_groups": [],
    "has_exclusions": true,
    "requires_mfa": true,
}

_mfa_privileged_roles_all_apps := {
    "id": "policy-003",
    "display_name": "Require MFA for privileged roles",
    "state": "enabled",
    "targets_all_users": false,
    "targets_all_apps": true,
    "include_roles": ["62e90394-69f5-4237-9190-012177145e10"],
    "include_roles_count": 1,
    "exclude_users": [],
    "exclude_groups": [],
    "has_exclusions": false,
    "requires_mfa": true,
}

_mfa_all_users_specific_apps_only := {
    "id": "policy-004",
    "display_name": "Require MFA - specific apps only",
    "state": "enabled",
    "targets_all_users": true,
    "targets_all_apps": false,
    "include_apps": ["00000002-0000-0ff1-ce00-000000000000"],
    "include_roles": [],
    "include_roles_count": 0,
    "exclude_users": [],
    "exclude_groups": [],
    "has_exclusions": false,
    "requires_mfa": true,
}

# ---------------------------------------------------------------------------
# Test: compliant — MFA for all users, all apps, no exclusions
# ---------------------------------------------------------------------------

test_compliant_mfa_all_users_all_apps if {
    result := data.essential_eight.asd_essential_eight.v2025.control_e8_mfa_2_1.result with input as {
        "total_policies": 3,
        "enabled_policies_count": 2,
        "mfa_policies_count": 1,
        "policies_requiring_mfa_for_all_users": [_mfa_all_users_all_apps],
        "policies_requiring_mfa_for_privileged_roles": [],
        "privileged_roles_count": 3,
        "all_mfa_policy_names": ["Require MFA for all users"],
    }
    result.compliant == true
    result.details.qualifying_policies_count == 1
    result.details.exclusions_detected == false
    contains(result.message, "MFA is enforced")
}

# ---------------------------------------------------------------------------
# Test: compliant — MFA for privileged roles only, all apps
# ---------------------------------------------------------------------------

test_compliant_mfa_privileged_roles_all_apps if {
    result := data.essential_eight.asd_essential_eight.v2025.control_e8_mfa_2_1.result with input as {
        "total_policies": 2,
        "enabled_policies_count": 1,
        "mfa_policies_count": 1,
        "policies_requiring_mfa_for_all_users": [],
        "policies_requiring_mfa_for_privileged_roles": [_mfa_privileged_roles_all_apps],
        "privileged_roles_count": 2,
        "all_mfa_policy_names": ["Require MFA for privileged roles"],
    }
    result.compliant == true
    result.details.qualifying_policies_count == 1
}

# ---------------------------------------------------------------------------
# Test: compliant with warning — exclusions present but policy still qualifies
# ---------------------------------------------------------------------------

test_compliant_with_exclusions_flagged if {
    result := data.essential_eight.asd_essential_eight.v2025.control_e8_mfa_2_1.result with input as {
        "total_policies": 3,
        "enabled_policies_count": 2,
        "mfa_policies_count": 1,
        "policies_requiring_mfa_for_all_users": [_mfa_all_users_all_apps_with_exclusions],
        "policies_requiring_mfa_for_privileged_roles": [],
        "privileged_roles_count": 3,
        "all_mfa_policy_names": ["Require MFA - with exclusions"],
    }
    # Compliant because policy exists, but exclusion warning is raised
    result.compliant == true
    result.details.exclusions_detected == true
    count(result.details.policies_with_exclusions) == 1
    contains(result.message, "exclusions that should be reviewed")
}

# ---------------------------------------------------------------------------
# Test: non-compliant — MFA policy exists but only covers specific apps (not all M365)
# ---------------------------------------------------------------------------

test_non_compliant_mfa_specific_apps_only if {
    result := data.essential_eight.asd_essential_eight.v2025.control_e8_mfa_2_1.result with input as {
        "total_policies": 2,
        "enabled_policies_count": 1,
        "mfa_policies_count": 1,
        "policies_requiring_mfa_for_all_users": [_mfa_all_users_specific_apps_only],
        "policies_requiring_mfa_for_privileged_roles": [],
        "privileged_roles_count": 2,
        "all_mfa_policy_names": ["Require MFA - specific apps only"],
    }
    result.compliant == false
    result.details.qualifying_policies_count == 0
    contains(result.message, "No enabled Conditional Access policy found")
}

# ---------------------------------------------------------------------------
# Test: non-compliant — no MFA policies at all
# ---------------------------------------------------------------------------

test_non_compliant_no_mfa_policies if {
    result := data.essential_eight.asd_essential_eight.v2025.control_e8_mfa_2_1.result with input as {
        "total_policies": 5,
        "enabled_policies_count": 5,
        "mfa_policies_count": 0,
        "policies_requiring_mfa_for_all_users": [],
        "policies_requiring_mfa_for_privileged_roles": [],
        "privileged_roles_count": 4,
        "all_mfa_policy_names": [],
    }
    result.compliant == false
    result.details.mfa_policies_count == 0
}

# ---------------------------------------------------------------------------
# Test: non-compliant — no Conditional Access policies exist at all
# ---------------------------------------------------------------------------

test_non_compliant_no_policies if {
    result := data.essential_eight.asd_essential_eight.v2025.control_e8_mfa_2_1.result with input as {
        "total_policies": 0,
        "enabled_policies_count": 0,
        "mfa_policies_count": 0,
        "policies_requiring_mfa_for_all_users": [],
        "policies_requiring_mfa_for_privileged_roles": [],
        "privileged_roles_count": 0,
        "all_mfa_policy_names": [],
    }
    result.compliant == false
}

# ---------------------------------------------------------------------------
# Test: details include correct evidence fields
# ---------------------------------------------------------------------------

test_result_details_structure if {
    result := data.essential_eight.asd_essential_eight.v2025.control_e8_mfa_2_1.result with input as {
        "total_policies": 3,
        "enabled_policies_count": 2,
        "mfa_policies_count": 1,
        "policies_requiring_mfa_for_all_users": [_mfa_all_users_all_apps],
        "policies_requiring_mfa_for_privileged_roles": [],
        "privileged_roles_count": 3,
        "all_mfa_policy_names": ["Require MFA for all users"],
    }
    # All expected evidence keys are present
    _ = result.details.total_ca_policies
    _ = result.details.enabled_ca_policies
    _ = result.details.mfa_policies_count
    _ = result.details.qualifying_policies_count
    _ = result.details.qualifying_policy_names
    _ = result.details.policies_with_exclusions
    _ = result.details.exclusions_detected
    _ = result.details.privileged_roles_in_tenant
    _ = result.details.all_mfa_policy_names
}
