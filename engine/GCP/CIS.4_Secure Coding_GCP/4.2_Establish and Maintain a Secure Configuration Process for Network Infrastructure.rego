# METADATA
# title: Establish and Maintain a Secure Configuration Process for Network Infrastructure (GCP)
# description: |
#   Technical and governance controls must ensure that a documented,
#   approved, and repeatable secure configuration process is established
#   and maintained for network infrastructure.
#
#   In a Google Cloud environment, network infrastructure is represented
#   primarily through centrally managed network policies and rule sets,
#   including hierarchical firewall policies, VPC firewall rules, and
#   Cloud DNS policies where relevant.
#
#   The secure network configuration process must establish:
#   - A documented network hardening standard
#   - A default-deny posture with controlled exceptions
#   - Approved ports and protocols
#   - Approved internet-facing network patterns
#   - Required firewall logging
#   - Controlled and traceable firewall rule changes
#   - Periodic rule recertification
#
#   Google Cloud implementation uses:
#   - Hierarchical firewall policies for centrally managed controls
#   - VPC firewall rules for network traffic enforcement
#   - Standardized network templates for common network patterns
#   - Cloud DNS policies where relevant
#   - Cloud Logging for firewall rule logging
#   - Cloud Audit Logs for network policy change history
#
#   The control verifies:
#   - A documented network configuration standard exists
#   - Network configuration documentation is approved and reviewed
#   - Firewall policy attachment and scope are defined
#   - Effective firewall rules are available for assessment
#   - A default-deny posture is established
#   - Network rule exceptions are scoped and justified
#   - Logging is enabled for high-impact rules
#   - Firewall rule changes are governed and traceable
#   - Internet-facing rules are periodically recertified
#
# related_resources:
# - ref: https://cloud.google.com/firewall/docs/firewall-policies
#   description: Hierarchical Firewall Policies Documentation
# - ref: https://cloud.google.com/vpc/docs/firewalls
#   description: VPC Firewall Rules Documentation
# - ref: https://cloud.google.com/logging/docs/audit
#   description: Cloud Audit Logs Documentation
# - ref: https://cloud.google.com/logging/docs
#   description: Cloud Logging Documentation
# - ref: https://cloud.google.com/dns/docs/policies
#   description: Cloud DNS Policies Documentation
#
# custom:
#   control_id: CIS-4.2
#   framework: cis
#   benchmark: gcp-foundations
#   version: v2.0.0
#   safeguard: 4.2
#   severity: high
#   service: VPC Firewall / Hierarchical Firewall Policies
#   asset_type: Documentation
#   implementation_group: 1
#   requires_permissions:
#   - compute.firewallPolicies.list
#   - compute.firewalls.list
#   - compute.networks.list
#   - logging.viewer
#   - logging.logEntries.list
#   - dns.policies.list

package cis.gcp_foundations.v2_0_0.control_4_2

import rego.v1

# ---------------------------
# Default Result
# ---------------------------
default compliant := false

default result := {
    "compliant": false,
    "message": "Evaluation failed: insufficient secure network configuration process evidence",
    "details": {}
}

# ---------------------------
# Compliance Logic
# ---------------------------
compliant if {
    input.network_configuration_process_defined == true
    input.network_configuration_scope_defined == true
    network_configuration_document_verified
    firewall_policy_scope_verified
    default_deny_posture_verified
    firewall_logging_verified
    change_governance_verified
    rule_recertification_verified
}

# ---------------------------
# Validate Network Configuration Documentation
# ---------------------------
network_configuration_document_verified if {
    input.network_configuration_document_title != ""
    input.network_configuration_document_version != ""
    input.network_configuration_approval_date != ""
    input.network_configuration_review_date != ""
    input.default_deny_standard_defined == true
    input.approved_ports_protocols_defined == true
    input.internet_facing_patterns_defined == true
    input.required_logging_defined == true
}

# ---------------------------
# Validate Network Configuration Scope
# ---------------------------
network_configuration_scope_defined if {
    input.network_configuration_scope != ""
    input.organization_scope != ""
    input.vpc_scope != ""
}

# ---------------------------
# Validate Firewall Policy Attachment and Scope
# ---------------------------
firewall_policy_scope_verified if {
    input.firewall_policy_attachment_verified == true
    input.firewall_policy_scope != ""
    input.effective_firewall_rules_available == true
}

# ---------------------------
# Validate Default-Deny Posture
# ---------------------------
default_deny_posture_verified if {
    input.default_deny_posture_enabled == true
    input.scoped_exceptions_defined == true
    input.exception_justification_available == true
}

# ---------------------------
# Validate Firewall Logging
# ---------------------------
firewall_logging_verified if {
    input.firewall_logging_enabled == true
    input.high_impact_rules_logging_enabled == true
    input.sample_firewall_logs_available == true
    input.sample_log_timestamp != ""
    input.sample_log_rule_name != ""
    input.sample_log_action != ""
}

# ---------------------------
# Validate Change Governance
# ---------------------------
change_governance_verified if {
    input.firewall_change_governance_enabled == true
    input.peer_review_required == true
    input.rule_change_approval_required == true
    input.change_history_available == true
    input.change_approver != ""
    input.change_date != ""
}

# ---------------------------
# Validate Rule Recertification
# ---------------------------
rule_recertification_verified if {
    input.periodic_rule_recertification_enabled == true
    input.internet_facing_rules_reviewed == true
    input.recertification_record_available == true
    input.recertification_date != ""
    input.recertification_owner != ""
}

# ---------------------------
# Result Output
# ---------------------------
result := output if {

    policies := get_array(input, "firewall_policies")
    rules := get_array(input, "firewall_rules")
    exceptions := get_array(input, "firewall_exceptions")

    output := {
        "compliant": compliant,
        "message": generate_message,
        "affected_resources": rules,
        "details": {
            "network_configuration_process_defined": input.network_configuration_process_defined,
            "network_configuration_scope": input.network_configuration_scope,
            "network_configuration_document_title": input.network_configuration_document_title,
            "network_configuration_document_version": input.network_configuration_document_version,
            "network_configuration_approval_date": input.network_configuration_approval_date,
            "network_configuration_review_date": input.network_configuration_review_date,
            "default_deny_standard_defined": input.default_deny_standard_defined,
            "approved_ports_protocols_defined": input.approved_ports_protocols_defined,
            "internet_facing_patterns_defined": input.internet_facing_patterns_defined,
            "required_logging_defined": input.required_logging_defined,
            "firewall_policy_attachment_verified": input.firewall_policy_attachment_verified,
            "firewall_policy_scope": input.firewall_policy_scope,
            "effective_firewall_rules_available": input.effective_firewall_rules_available,
            "default_deny_posture_enabled": input.default_deny_posture_enabled,
            "scoped_exceptions_defined": input.scoped_exceptions_defined,
            "firewall_logging_enabled": input.firewall_logging_enabled,
            "high_impact_rules_logging_enabled": input.high_impact_rules_logging_enabled,
            "firewall_policy_count": count(policies),
            "firewall_rule_count": count(rules),
            "firewall_exception_count": count(exceptions),
            "firewall_change_governance_enabled": input.firewall_change_governance_enabled,
            "peer_review_required": input.peer_review_required,
            "rule_change_approval_required": input.rule_change_approval_required,
            "change_history_available": input.change_history_available,
            "periodic_rule_recertification_enabled": input.periodic_rule_recertification_enabled,
            "internet_facing_rules_reviewed": input.internet_facing_rules_reviewed,
            "recertification_date": input.recertification_date,
            "recertification_owner": input.recertification_owner,
            "requires_sample_evidence": true
        }
    }
}

# ---------------------------
# Message Logic
# ---------------------------
generate_message := msg if {
    not input.network_configuration_process_defined
    msg := "FAIL: Secure network configuration process is not defined"
}

generate_message := msg if {
    input.network_configuration_process_defined
    not input.network_configuration_scope_defined
    msg := "FAIL: Network configuration scope is not defined"
}

generate_message := msg if {
    input.network_configuration_scope_defined
    not network_configuration_document_verified
    msg := "FAIL: Network configuration standard is missing approval, review, or required hardening requirements"
}

generate_message := msg if {
    network_configuration_document_verified
    not firewall_policy_scope_verified
    msg := "INCONCLUSIVE: Firewall rules are available but policy attachment or scope evidence is missing"
}

generate_message := msg if {
    firewall_policy_scope_verified
    not default_deny_posture_verified
    msg := "FAIL: Default-deny posture or justification for scoped exceptions is not established"
}

generate_message := msg if {
    default_deny_posture_verified
    not firewall_logging_verified
    msg := "FAIL: Firewall logging is not enabled or high-impact rule logging evidence is missing"
}

generate_message := msg if {
    firewall_logging_verified
    not change_governance_verified
    msg := "FAIL: Firewall rule changes cannot be traced to a peer review and approval workflow"
}

generate_message := msg if {
    change_governance_verified
    not rule_recertification_verified
    msg := "FAIL: Periodic recertification evidence for internet-facing firewall rules is missing"
}

generate_message := msg if {
    network_configuration_document_verified
    not firewall_policy_scope_verified
    msg := "INCONCLUSIVE: Governance documentation exists but firewall policy attachment and scope cannot be verified"
}

generate_message := msg if {
    firewall_policy_scope_verified
    not input.effective_firewall_rules_available
    msg := "INCONCLUSIVE: Firewall policy scope is visible but a complete effective rule export is unavailable"
}

generate_message := msg if {
    rule_recertification_verified
    compliant
    msg := "PASS: Secure network configuration is documented, default-deny controls are enforced, firewall activity is logged, changes are governed, and rules are periodically recertified"
}

# ---------------------------
# Helper Functions
# ---------------------------
get_array(obj, key) := value if {
    value := obj[key]
} else := []
