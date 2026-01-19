# METADATA
# title: Ensure that DKIM is enabled for all Exchange Online Domains
# description: |
#   DKIM is one of the trio of Authentication methods (SPF, DKIM and DMARC) that help 
#   prevent attackers from sending messages that look like they come from your domain. 
#  
# related_resources:
# - ref: https://www.cisecurity.org/benchmark/microsoft_365
#   description: CIS Microsoft 365 Foundations Benchmark
# custom:
#   control_id: CIS-2.1.9
#   framework: cis
#   benchmark: microsoft-365-foundations
#   version: v6.0.0
#   severity: high
#   service: Exchange
#   requires_permissions:
#   - Exchange.Manage

package cis.microsoft_365_foundations.v6_0_0.control_2_1_9

default result := {"compliant": false, "message": "Evaluation failed"}

# Compute dkim_enabled from per-domain lists
dkim_enabled := true if count(input.domains_with_dkim_disabled) == 0
dkim_enabled := false if count(input.domains_with_dkim_disabled) > 0
dkim_enabled := null if { 
    not input.domains_with_dkim_enabled
    not input.domains_with_dkim_disabled
}

result := output if {
    compliant := dkim_enabled == true

    output := {
        "compliant": compliant,
        "message": generate_message(dkim_enabled),
        "affected_resources": generate_affected_resources(dkim_enabled, input),
        "details": {
            "dkim_signing_enabled": dkim_enabled,
            "domains_with_dkim_enabled": input.domains_with_dkim_enabled,
            "domains_with_dkim_disabled": input.domains_with_dkim_disabled
        }
    }
}

generate_message(dkim_enabled) := msg if {
    dkim_enabled == true
    msg := "DKIM signing is enabled for Exchange Online domains"
}

generate_message(dkim_enabled) := msg if {
    dkim_enabled == false
    msg := "DKIM signing is disabled for Exchange Online domains"
}

generate_message(dkim_enabled) := msg if {
    dkim_enabled == null
    msg := "Unable to determine DKIM signing status"
}

generate_affected_resources(true, _) := []
generate_affected_resources(false, data_input) := data_input.domains_with_dkim_disabled
generate_affected_resources(null, _) := ["DKIM signing status unknown"]
