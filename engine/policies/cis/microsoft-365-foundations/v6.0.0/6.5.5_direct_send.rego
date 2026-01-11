# METADATA
# title: Ensure Direct Send submissions are rejected
# description: |
#   Direct Send allows anonymous SMTP connections to send email as the
#   organization. This can be exploited for phishing and spoofing attacks.
#   Configure transport settings to reject unauthenticated direct send.
# related_resources:
# - ref: https://www.cisecurity.org/benchmark/microsoft_365
#   description: CIS Microsoft 365 Foundations Benchmark
# custom:
#   control_id: CIS-6.5.5
#   framework: cis
#   benchmark: microsoft-365-foundations
#   version: v6.0.0
#   severity: medium
#   service: Exchange
#   requires_permissions:
#   - Exchange.Manage

package cis.microsoft_365_foundations.v6_0_0.control_6_5_5

default result := {"compliant": false, "message": "Evaluation failed"}

result := output if {
    reject_direct_send := input.reject_direct_send

    # Compliant when RejectDirectSend is true
    compliant := reject_direct_send == true

    output := {
        "compliant": compliant,
        "message": generate_message(reject_direct_send),
        "affected_resources": generate_affected_resources(compliant),
        "details": {
            "reject_direct_send": reject_direct_send
        }
    }
}

generate_message(reject_direct_send) := msg if {
    reject_direct_send == true
    msg := "Direct Send submissions are rejected"
}

generate_message(reject_direct_send) := msg if {
    reject_direct_send == false
    msg := "Direct Send submissions are allowed (RejectDirectSend is False)"
}

generate_message(reject_direct_send) := msg if {
    reject_direct_send == null
    msg := "Unable to determine Direct Send status"
}

generate_affected_resources(true) := []
generate_affected_resources(false) := ["Direct Send submissions are allowed"]
