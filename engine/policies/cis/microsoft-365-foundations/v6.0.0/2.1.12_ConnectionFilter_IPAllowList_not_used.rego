# METADATA
# title: Ensure the connection filter IP allow list is not used
# description: |
#   In Microsoft 365 organizations with Exchange Online mailboxes or standalone
#   Exchange Online Protection organizations without Exchange Online mailboxes
#   connection filtering and the default connection filter policy identify good or
#   bad source email servers by IP addresses. The key components of the default connection
#   filter policy are IP Allow List, IP Block List and Safe list.
#   The recommended state is IP Allow List empty or undefined.
#  
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

# Required IPAllowList setting
required_fields := {
    "IPAllowList": []
}

ip_allow_list_is_empty := true if {
    input.IPAllowList == []  # empty array
}

ip_allow_list_is_empty := true if {
    input.IPAllowList == {}  # empty object
}

ip_allow_list_is_empty := false if {
    input.IPAllowList != []  # non-empty array
}

ip_allow_list_is_empty := false if {
    input.IPAllowList != {}  # non-empty object
}

ip_allow_list_is_empty := null if {
    not input.IPAllowList  # field is missing
}

result := output if {
    compliant := ip_allow_list_is_empty == true

    output := {
        "compliant": compliant,
        "message": generate_message(ip_allow_list_is_empty),
        "affected_resources": generate_affected_resources(ip_allow_list_is_empty),
        "details": {
            "IPAllowList": input.IPAllowList
        }
    }
}

generate_message(true) := "IPAllowList is empty or {} in Exchange Online Hosted Connection Filter"
generate_message(false) := "IPAllowList is not empty or is not {} in Exchange Online Hosted Connection Filter"
generate_message(null) := "Unable to determine the IPAllowList status in Exchange Online Hosted Connection Filter"

generate_affected_resources(true) := []
generate_affected_resources(false) := ["HostedConnectionFilterPolicy"]
generate_affected_resources(null) := ["HostedConnectionFilterPolicy status unknown"]
