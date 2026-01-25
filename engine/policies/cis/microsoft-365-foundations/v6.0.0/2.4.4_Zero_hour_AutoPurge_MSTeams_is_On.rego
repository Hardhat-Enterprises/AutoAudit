# METADATA
# title: Ensure Zero-hour auto purge for Microsoft Teams is on
# description: |
#  Zero-hour auto purge is a protection feature that retroactively detects
#  and neutralizes malware and high-confidence phishing. When ZAP for Teams protection
#  blocks a message, the message is blocked for everyone in the chat.
#  The initial block happens right after delivery, but ZAP occurs up to 48 hours after delivery.
#  
# related_resources:
# - ref: https://www.cisecurity.org/benchmark/microsoft_365
#   description: CIS Microsoft 365 Foundations Benchmark
# custom:
#   control_id: CIS-2.4.4
#   framework: cis
#   benchmark: microsoft-365-foundations
#   version: v6.0.0
#   severity: medium
#   service: Exchange
#   requires_permissions:
#   - Exchange.Manage

package cis.microsoft_365_foundations.v6_0_0.control_2_4_4

import rego.v1

zap_enabled := object.get(input, "zap_enabled", null)

zero_hour_auto_purge_enabled := true if zap_enabled == true
zero_hour_auto_purge_enabled := false if zap_enabled == false
zero_hour_auto_purge_enabled := null if zap_enabled == null

result := output if {
    compliant := zero_hour_auto_purge_enabled == true

    output := {
        "compliant": compliant,
        "message": generate_message(zero_hour_auto_purge_enabled),
        "affected_resources": generate_affected_resources(zero_hour_auto_purge_enabled),
        "details": {
            "zap_enabled": zap_enabled
        }
    }
}

generate_message(true) := "Zero-hour auto purge is enabled for Microsoft Teams"
generate_message(false) := "Zero-hour auto purge is not enabled for Microsoft Teams"
generate_message(null) := "Unable to determine Zero-hour auto purge status for Microsoft Teams"
generate_affected_resources(true) := []
generate_affected_resources(false) := ["TeamsProtectionPolicy"]
generate_affected_resources(null) := ["TeamsProtectionPolicy status unknown"]
