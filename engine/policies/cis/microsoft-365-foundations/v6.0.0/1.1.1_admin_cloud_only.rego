# METADATA
# title: Ensure Administrative accounts are cloud-only
# description: |
#   Administrative accounts should not be synced from on-premises Active Directory.
#   Cloud-only accounts reduce the attack surface by not being tied to on-premises
#   infrastructure, preventing lateral movement from compromised on-prem environments.
# related_resources:
# - ref: https://www.cisecurity.org/benchmark/microsoft_365
#   description: CIS Microsoft 365 Foundations Benchmark
# custom:
#   control_id: CIS-1.1.1
#   framework: cis
#   benchmark: microsoft-365-foundations
#   version: v6.0.0
#   severity: critical
#   service: EntraID
#   requires_permissions:
#   - User.Read.All
#   - RoleManagement.Read.Directory

package cis.microsoft_365_foundations.v6_0_0.control_1_1_1

import rego.v1

default result := {
    "compliant": false,
    "message": "Evaluation failed: unable to retrieve administrative account data",
    "details": {}
}

# Main evaluation rule
result := output if {
    admin_accounts := get_array(input, "admin_accounts")
    synced_admins := [a | some a in admin_accounts; a.on_premises_sync_enabled == true]

    compliant := count(synced_admins) == 0

    msg := build_message(admin_accounts, synced_admins)
    affected := [a.userPrincipalName | some a in synced_admins]

    output := {
        "compliant": compliant,
        "message": msg,
        "affected_resources": affected,
        "details": {
            "total_admin_accounts": count(admin_accounts),
            "synced_admin_count": count(synced_admins),
            "cloud_only_admin_count": count(admin_accounts) - count(synced_admins),
            "synced_admins": [{"userPrincipalName": a.userPrincipalName, "displayName": a.displayName, "admin_roles": a.admin_roles} | some a in synced_admins]
        }
    }
}

# Helper to get array with default
get_array(obj, key) := value if {
    value := obj[key]
} else := []

build_message(all_admins, synced_admins) := msg if {
    count(synced_admins) == 0
    msg := sprintf("All %d administrative account(s) are cloud-only", [count(all_admins)])
}

build_message(all_admins, synced_admins) := msg if {
    count(synced_admins) > 0
    msg := sprintf("%d of %d administrative account(s) are synced from on-premises AD", [count(synced_admins), count(all_admins)])
}
