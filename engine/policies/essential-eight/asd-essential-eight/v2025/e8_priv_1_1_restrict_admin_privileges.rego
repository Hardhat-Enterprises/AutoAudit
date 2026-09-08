# METADATA
# title: Essential Eight - Privileged access restricted and appropriately assigned
# description: |
#   Checks whether administrative privileges are limited to an appropriate set
#   of users by evaluating Entra ID directory role assignments.
#   Assesses two dimensions: whether all privileged accounts are cloud-only,
#   and whether the number of privileged users is within an appropriate threshold.
#   Research reference: 26T1-SEC-EG-002, 26T1-SEC-EG-004
# custom:
#   control_id: E8-PRIV-1.1
#   framework: essential-eight
#   benchmark: asd-essential-eight
#   version: v2025
#   severity: critical
#   service: EntraID
#   requires_permissions:
#   - RoleManagement.Read.Directory
#   - User.Read.All

package essential_eight.asd_essential_eight.v2025.control_e8_priv_1_1

import rego.v1

MAX_ADMIN_ACCOUNTS := 5

synced_accounts := [a |
    some a in input.admin_accounts
    a.on_premises_sync_enabled == true
]

is_compliant := false if {
    input.total_admin_accounts == 0
}

is_compliant := true if {
    input.total_admin_accounts > 0
    count(synced_accounts) == 0
    input.total_admin_accounts <= MAX_ADMIN_ACCOUNTS
}

is_compliant := false if {
    input.total_admin_accounts > 0
    count(synced_accounts) > 0
}

is_compliant := false if {
    input.total_admin_accounts > MAX_ADMIN_ACCOUNTS
}

default is_compliant := false

result := {
    "compliant": is_compliant,
    "message": message,
    "details": {
        "total_admin_accounts": input.total_admin_accounts,
        "cloud_only_admin_count": input.cloud_only_admin_count,
        "synced_admin_count": input.synced_admin_count,
        "synced_accounts": [a.userPrincipalName | some a in synced_accounts],
        "threshold": MAX_ADMIN_ACCOUNTS,
        "threshold_exceeded": input.total_admin_accounts > MAX_ADMIN_ACCOUNTS,
    },
}

message := "No admin accounts detected - check collector permissions" if {
    input.total_admin_accounts == 0
}

message := sprintf(
    "Privileged access appears appropriately restricted: %d admin account(s) found, all cloud-only",
    [input.total_admin_accounts],
) if {
    input.total_admin_accounts > 0
    is_compliant == true
}

message := sprintf(
    "%d privileged account(s) are synced from on-premises Active Directory and not cloud-only",
    [count(synced_accounts)],
) if {
    input.total_admin_accounts > 0
    count(synced_accounts) > 0
}

message := sprintf(
    "Privileged access appears excessive: %d admin account(s) found, exceeding the threshold of %d",
    [input.total_admin_accounts, MAX_ADMIN_ACCOUNTS],
) if {
    input.total_admin_accounts > 0
    count(synced_accounts) == 0
    input.total_admin_accounts > MAX_ADMIN_ACCOUNTS
}

default message := "Unable to evaluate privileged access: no admin account data available"
