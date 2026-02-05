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
#   version: v3.1.0
#   severity: critical
#   service: EntraID
#   requires_permissions:
#   - User.Read.All
#   - RoleManagement.Read.Directory

package cis.microsoft_365_foundations.v3_1_0.control_1_1_1

default result := {"compliant": false, "message": "Evaluation failed"}

result := output if {
    synced_admins := [a | some a in input.admin_accounts; a.on_premises_sync_enabled == true]
    output := {
        "compliant": count(synced_admins) == 0,
        "message": generate_message(synced_admins, input.admin_accounts),
        "affected_resources": [a.userPrincipalName | some a in synced_admins],
        "details": {
            "total_admin_accounts": count(input.admin_accounts),
            "synced_admin_count": count(synced_admins),
            "cloud_only_admin_count": count(input.admin_accounts) - count(synced_admins)
        }
    }
}

generate_message(synced_admins, all_admins) := msg if {
    count(synced_admins) == 0
    msg := sprintf("All %d administrative accounts are cloud-only", [count(all_admins)])
}

generate_message(synced_admins, all_admins) := msg if {
    count(synced_admins) > 0
    msg := sprintf("%d of %d administrative accounts are synced from on-premises AD", [count(synced_admins), count(all_admins)])
}
