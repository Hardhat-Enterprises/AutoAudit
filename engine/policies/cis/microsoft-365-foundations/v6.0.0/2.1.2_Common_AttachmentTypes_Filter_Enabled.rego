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

default result := {"compliant": false, "message": "Evaluation failed"}

enable_file_filter := object.get(
    input,
    "enable_file_filter",
    object.get(object.get(input, "default_policy", {}), "EnableFileFilter", null)
)

file_filter_enabled := true if enable_file_filter == true
file_filter_enabled := false if enable_file_filter != true
file_filter_enabled := null if enable_file_filter == null

result := output if {
    compliant := file_filter_enabled == true

    output := {
        "compliant": compliant,
        "message": generate_message(file_filter_enabled),
        "affected_resources": generate_affected_resources(file_filter_enabled, input),
        "details": {
            "enable_file_filter": file_filter_enabled
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

generate_message(file_filter_enabled) := msg if {
    file_filter_enabled == null
    msg := "Unable to determine the 'Enable the common attachments filter' status."
}

generate_affected_resources(true, _) := []
generate_affected_resources(false, data_input) := ["Common attachments filter is disabled"]
generate_affected_resources(null, _) := ["Common attachments filter status unknown"]
