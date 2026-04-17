# METADATA
# title: Ensure sign-in to shared mailboxes is blocked
# description: |
#   Shared mailboxes should not allow direct sign-in. Enabling sign-in on a
#   shared mailbox creates an unnecessary authentication surface that bypasses
#   individual user accountability and increases the risk of credential abuse.
# related_resources:
# - ref: https://www.cisecurity.org/benchmark/microsoft_365
#   description: CIS Microsoft 365 Foundations Benchmark
# custom:
#   control_id: CIS-1.2.2
#   framework: cis
#   benchmark: microsoft-365-foundations
#   version: v6.0.0
#   severity: medium
#   service: Exchange
#   requires_permissions:
#   - Exchange.Manage

package cis.microsoft_365_foundations.v6_0_0.control_1_2_2

import rego.v1

default result := {
    "compliant": false,
    "message": "Evaluation failed: unable to retrieve shared mailbox data",
    "details": {},
}

result := output if {
    mailboxes := get_array(input, "shared_mailboxes")
    violating := [m |
        some m in mailboxes
        object.get(m, "SignInBlocked", null) != true
    ]

    compliant := count(violating) == 0
    msg := build_message(mailboxes, violating)
    affected := [m.UserPrincipalName |
        some m in violating
        m.UserPrincipalName != null
    ]

    output := {
        "compliant": compliant,
        "message": msg,
        "affected_resources": affected,
        "details": {
            "total_shared_mailboxes": count(mailboxes),
            "violating_count": count(violating),
            "violations": [
                {
                    "UserPrincipalName": m.UserPrincipalName,
                    "DisplayName": object.get(m, "DisplayName", null),
                    "SignInBlocked": object.get(m, "SignInBlocked", null),
                } |
                some m in violating
            ],
        },
    }
}

get_array(obj, key) := value if {
    value := obj[key]
} else := []

build_message(all_mailboxes, violating) := msg if {
    count(violating) == 0
    msg := sprintf("All %d shared mailbox(es) have sign-in blocked", [count(all_mailboxes)])
}

build_message(_, violating) := msg if {
    count(violating) > 0
    msg := sprintf("%d shared mailbox(es) do not have sign-in blocked", [count(violating)])
}
