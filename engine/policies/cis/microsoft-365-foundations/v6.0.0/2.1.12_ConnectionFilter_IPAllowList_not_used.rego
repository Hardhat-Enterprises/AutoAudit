# METADATA
# title: Ensure the connection filter IP allow list is not used
# description: |
#   In Microsoft 365 organizations with Exchange Online mailboxes or standalone
#   Exchange Online Protection organizations without Exchange Online mailboxes,
#   connection filtering and the default connection filter policy identify good or
#   bad source email servers by IP addresses. The key components of the default connection
#   filter policy are IP Allow List, IP Block List and Safe list.
#   The recommended state is IP Allow List empty or undefined.
# related_resources:
# - ref: https://www.cisecurity.org/benchmark/microsoft_365
#   description: CIS Microsoft 365 Foundations Benchmark
# custom:
#   control_id: CIS-2.1.12
#   framework: cis
#   benchmark: microsoft-365-foundations
#   version: v6.0.0
#   severity: medium
#   service: Exchange
#   requires_permissions:
#   - Exchange.Manage

package cis.microsoft_365_foundations.v6_0_0.control_2_1_12

default result := {"compliant": false, "message": "Evaluation failed"}

ip_allow_list_status := "empty" if input.ip_allow_list == []
ip_allow_list_status := "not_empty" if input.ip_allow_list != []

result := {
    "compliant": ip_allow_list_status == "empty",
    "message": messages[ip_allow_list_status],
    "affected_resources": affected_resources[ip_allow_list_status],
    "details": {
        "ip_allow_list": input.ip_allow_list
    }
}

messages := {
    "empty": "IPAllowList is empty in Exchange Online Hosted Connection Filter",
    "not_empty": "IPAllowList is not empty in Exchange Online Hosted Connection Filter"
}

affected_resources := {
    "empty": [],
    "not_empty": ["HostedConnectionFilterPolicy"]
}
