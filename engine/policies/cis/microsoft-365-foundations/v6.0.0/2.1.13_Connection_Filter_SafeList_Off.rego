# METADATA
# title: Ensure the connection filter safe list is off
# description: |
#   In Microsoft 365 organizations with Exchange Online mailboxes or standalone
#   Exchange Online Protection organizations without Exchange Online mailboxes
#   connection filtering and the default connection filter policy identify good or bad
#   source email servers by IP addresses. The key components of the default connection
#   filter policy are IP Allow List, IP Block List and Safe list.
#   The safe list is a pre-configured allow list that is dynamically updated by Microsoft.
#   The recommended safe list state is: Off or False
#  
# related_resources:
# - ref: https://www.cisecurity.org/benchmark/microsoft_365
#   description: CIS Microsoft 365 Foundations Benchmark
# custom:
#   control_id: CIS-2.1.13
#   framework: cis
#   benchmark: microsoft-365-foundations
#   version: v6.0.0
#   severity: medium
#   service: Exchange
#   requires_permissions:
#   - Exchange.Manage

package cis.microsoft_365_foundations.v6_0_0.control_2_1_13

default result := {"compliant": false, "message": "Evaluation failed"}

# Required EnableSafeList setting
required_fields := {
    "EnableSafeList": false
}

enable_safe_list_is_false := true if {
    input.EnableSafeList == false  # Ensure EnableSafeList is False
}

enable_safe_list_is_false := false if {
    input.EnableSafeList == true  # If EnableSafeList is True, it's non-compliant
}

enable_safe_list_is_false := null if {
    not input.EnableSafeList  # If EnableSafeList is missing, return null
}

result := output if {
    compliant := enable_safe_list_is_false == true

    output := {
        "compliant": compliant,
        "message": generate_message(enable_safe_list_is_false),
        "affected_resources": generate_affected_resources(enable_safe_list_is_false),
        "details": {
            "EnableSafeList": input.EnableSafeList
        }
    }
}

generate_message(true) := "EnableSafeList is False for Exchange Online Hosted Connection Filter"
generate_message(false) := "EnableSafeList is not False for Exchange Online Hosted Connection Filter"
generate_message(null) := "Unable to determine the EnableSafeList status in Exchange Online Hosted Connection Filter"

generate_affected_resources(true) := []
generate_affected_resources(false) := ["HostedConnectionFilterPolicy"]
generate_affected_resources(null) := ["HostedConnectionFilterPolicy status unknown"]
