# METADATA
# title: Restrict Unnecessary or Unauthorized Browser and Email Client Extensions (GCP)
# description: |
#   Organisations must restrict, either through uninstalling or disabling, any unauthorized or
#   unnecessary browser or email client plugins, extensions, and add-on applications. This is enforced
#   via Chrome enterprise extension policies, including allowlist/blocklist configuration, forced
#   installation of approved extensions, and restrictions on unmanaged installs and developer mode.
#   Policy scope (OU/group) must be confirmed, and a time-stamped extension inventory or violation
#   report must be provided as evidence that unauthorized or unmanaged extensions are being blocked
#   in practice.
# related_resources:
# - ref: https://support.google.com/chrome/a/answer/2657289
#   description: Chrome Enterprise Extension Policy Documentation
# - ref: https://support.google.com/chrome/a/answer/9296680
#   description: Chrome Extension Allowlist/Blocklist Configuration Documentation
# custom:
#   control_id: CIS-9.4
#   framework: cis
#   benchmark: gcp-foundations
#   version: v2.0.0
#   severity: medium
#   service: Chrome Browser Cloud Management
#   requires_permissions:
#   - chrome.policies.get
#   - chrome.reports.get
#   - admin.directory.orgunit.readonly

package cis.gcp_foundations.v2_0_0.control_9_4

import rego.v1

# Default result
default result := {
    "compliant": false,
    "message": "Evaluation failed: insufficient data to verify that unauthorised browser and email client extensions are blocked.",
    "details": {},
}

default compliant := false
 
# ---------------------------
# Compliance Logic
# ---------------------------
compliant if {
    chrome_extension_configured
    coverage_evidence_configured
    extension_evidence_shown
}

# extension controls must restrict both unauthorised allow/block-listed extensions and unmanaged installs/developer mode - 
# either gap leaves a path for unapproved extensions to run in managed browser profiles
chrome_extension_configured if {
    input.extension_allow_block_configured == true
    input.unmanaged_installs_restricted == true
}

# a policy with no identifiable OU/group target cannot be confirmed as applying to any specific population - 
# scope must be explicit, not assumed
coverage_evidence_configured if {
    input.extension_policy_scope_type != ""
    input.extension_policy_scope_identifier != ""
}

# either a time-stamped extension inventory or a violation report is acceptable as operational proof - 
# this safeguard only requires one, not both
extension_evidence_shown if {
    input.extension_inventory_date != ""
} else if {
    input.violation_report_date != ""
}

# ---------------------------
# Result Output
# ---------------------------
result := output if {
    extension_violation_examples := get_array(input, "extension_violation_examples")

    output := {
        "compliant": compliant,
        "message": generate_message,
        "affected_resources": extension_violation_examples,
        "details": {
            "extension_allow_block_configured": input.extension_allow_block_configured,
            "unmanaged_installs_restricted": input.unmanaged_installs_restricted,
            "extension_policy_scope_type": input.extension_policy_scope_type,
            "extension_policy_scope_identifier": input.extension_policy_scope_identifier,
            "extension_inventory_date": input.extension_inventory_date,
            "violation_report_date": input.violation_report_date,
            "extension_violation_examples_count": count(extension_violation_examples),
            "requires_example_evidence": true,
        }
    }
}

# ---------------------------
# Message Logic
# ---------------------------
generate_message := msg if {
    not chrome_extension_configured
    msg := "FAIL: No extension allowlist/blocklist policy or unmanaged install restriction is configured."
}

generate_message := msg if {
    chrome_extension_configured
    not coverage_evidence_configured
    msg := "INCONCLUSIVE: Extension policy is not confirmed as applied to a specific OU or group, so it cannot be confirmed as enforced for any particular population."
}

generate_message := msg if {
    chrome_extension_configured
    coverage_evidence_configured
    not extension_evidence_shown
    msg := "INCONCLUSIVE: No time-stamped extension inventory or violation report was found showing the restriction is actively enforced."
}

generate_message msg if {
    compliant
    msg := "PASS: Extension allowlist/blocklist and unmanaged install restrictions are configured, policy scope is confirmed and a recent inventory or violation report verifies the restriction is actively enforced."
}

# ---------------------------
# Helper Functions
# ---------------------------
get_array(obj, key) := value if {
    value := obj[key]
} else := []