# METADATA
# title: Ensure administrative accounts use licenses with a reduced application footprint
# description: |
#   Administrative accounts should use licenses that avoid broad user-application workloads
#   such as Exchange Online, Microsoft Teams, or Office desktop suites where identity-only
#   SKUs are sufficient.
# related_resources:
# - ref: https://www.cisecurity.org/benchmark/microsoft_365
#   description: CIS Microsoft 365 Foundations Benchmark
# custom:
#   control_id: CIS-1.1.4
#   framework: cis
#   benchmark: microsoft-365-foundations
#   version: v6.0.0
#   severity: medium
#   service: EntraID
#   requires_permissions:
#   - User.Read.All
#   - RoleManagement.Read.Directory

package cis.microsoft_365_foundations.v6_0_0.control_1_1_4

import rego.v1

default result := {
    "compliant": false,
    "message": "Evaluation failed: unable to retrieve administrative license data",
    "details": {},
}

result := output if {
    admin_accounts := get_array(input, "admin_accounts")
    violating := [a |
        some a in admin_accounts
        object.get(a, "uses_reduced_license_footprint", false) == false
    ]

    compliant := count(violating) == 0
    msg := build_message(admin_accounts, violating)
    affected := [a.userPrincipalName |
        some a in violating
        a.userPrincipalName != null
    ]

    output := {
        "compliant": compliant,
        "message": msg,
        "affected_resources": affected,
        "details": {
            "total_admin_accounts": count(admin_accounts),
            "violating_admin_count": count(violating),
            "violations": [{"userPrincipalName": a.userPrincipalName, "displayName": a.displayName, "high_footprint_service_plans_enabled": object.get(a, "high_footprint_service_plans_enabled", []), "sku_part_numbers": object.get(a, "sku_part_numbers", [])} |
                some a in violating
            ],
        },
    }
}

get_array(obj, key) := value if {
    value := obj[key]
} else := []

build_message(all_admins, violating) := msg if {
    count(violating) == 0
    msg := sprintf("All %d administrative account(s) use reduced license footprints", [count(all_admins)])
}

build_message(all_admins, violating) := msg if {
    count(violating) > 0
    msg := sprintf("%d of %d administrative account(s) have high-footprint application licenses enabled", [count(violating), count(all_admins)])
}
