# METADATA
# title: Ensure the Common Attachment Types Filter is enabled
# description: |
#   Common Attachment Types Filter lets a user block known and 
#   custom malicious file types from being attached to emails
#  
# related_resources:
# - ref: https://www.cisecurity.org/benchmark/microsoft_365
#   description: CIS Microsoft 365 Foundations Benchmark
# custom:
#   control_id: CIS-2.1.2
#   framework: cis
#   benchmark: microsoft-365-foundations
#   version: v6.0.0
#   severity: high
#   service: Exchange
#   requires_permissions:
#   - Exchange.Manage

package cis.microsoft_365_foundations.v6_0_0.control_2_1_2

import rego.v1

default result := {"compliant": false, "message": "Evaluation failed"}

file_filter_enabled := true if input.enable_file_filter == true
file_filter_enabled := false if input.enable_file_filter != true

result := output if {
    compliant := file_filter_enabled == true

    output := {
        "compliant": compliant,
        "message": generate_message(file_filter_enabled),
        "affected_resources": generate_affected_resources(file_filter_enabled),
        "details": {
            "enablefilefilter": file_filter_enabled
        }
    }
}

generate_message(file_filter_enabled) := msg if {
    file_filter_enabled == true
    msg := "The 'Enable the common attachments filter' is On."
}

generate_message(file_filter_enabled) := msg if {
    file_filter_enabled == false
    msg := "The 'Enable the common attachments filter' is Off."
}

generate_affected_resources(true) := []
generate_affected_resources(false) := ["Common attachments filter is disabled"]
