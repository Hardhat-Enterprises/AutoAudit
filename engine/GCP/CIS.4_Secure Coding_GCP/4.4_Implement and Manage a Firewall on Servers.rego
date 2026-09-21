# METADATA
# title: Implement and Manage a Firewall on Servers (GCP)
# description: |
#   Server assets must have a firewall implemented and managed where
#   supported. The firewall may be implemented using virtual firewalls,
#   operating system firewalls, or third-party firewall agents.
#
#   In Google Cloud, the authoritative server firewall control is typically
#   implemented through VPC firewall rules and, where applicable,
#   hierarchical firewall policies.
#
#   The control must establish:
#   - A default-deny inbound posture
#   - Explicit and tightly scoped allow rules
#   - Controlled ingress and egress access
#   - Firewall logging for internet-facing or high-risk rules
#   - Periodic review and maintenance of firewall rules
#   - Clear treatment of host-level firewalls
#
#   Google Cloud implementation uses:
#   - VPC firewall rules for server ingress and egress enforcement
#   - Hierarchical firewall policies for centrally managed controls
#   - Cloud Logging for firewall rule logging
#   - Cloud Armor security policies for HTTP(S) workloads where applicable
#   - OS Config / VM Manager OS Policies for host firewall enforcement
#
#   The control verifies:
#   - Effective firewall rules and policies are available
#   - Inbound traffic follows a default-deny posture
#   - Allow rules are tightly scoped
#   - High-risk firewall rules have logging enabled
#   - Cloud Armor is configured for applicable exposed web workloads
#   - Host firewall scope is explicitly defined
#   - Host firewalls are managed where they are claimed to be in scope
#   - Firewall rules are periodically reviewed
#   - Firewall changes and maintenance are traceable
#
# related_resources:
# - ref: https://cloud.google.com/vpc/docs/firewalls
#   description: VPC Firewall Rules Documentation
# - ref: https://cloud.google.com/firewall/docs/firewall-policies
#   description: Hierarchical Firewall Policies Documentation
# - ref: https://cloud.google.com/armor/docs
#   description: Cloud Armor Documentation
# - ref: https://cloud.google.com/logging/docs
#   description: Cloud Logging Documentation
# - ref: https://cloud.google.com/compute/vm-manager/docs/os-policies
#   description: VM Manager OS Policies Documentation
#
# custom:
#   control_id: CIS-4.4
#   framework: cis
#   benchmark: gcp-foundations
#   version: v2.0.0
#   safeguard: 4.4
#   severity: high
#   service: VPC Firewall / Hierarchical Firewall Policies
#   asset_type: Devices
#   implementation_group: 1
#   requires_permissions:
#   - compute.firewalls.list
#   - compute.firewallPolicies.list
#   - compute.networks.list
#   - logging.viewer
#   - logging.logEntries.list
#   - compute.backendServices.get
#   - osconfig.osPolicyAssignments.list

package cis.gcp_foundations.v2_0_0.control_4_4

import rego.v1

# ---------------------------
# Default Result
# ---------------------------
default compliant := false

default result := {
    "compliant": false,
    "message": "Evaluation failed: insufficient server firewall evidence",
    "details": {}
}

# ---------------------------
# Compliance Logic
# ---------------------------
compliant if {
    input.server_firewall_process_defined == true
    input.server_firewall_scope_defined == true
    effective_firewall_policy_verified
    default_deny_inbound_verified
    high_risk_logging_verified
    host_firewall_treatment_verified
    firewall_review_verified
}

# ---------------------------
# Validate Server Firewall Scope
# ---------------------------
server_firewall_scope_defined if {
    input.server_firewall_scope != ""
    input.in_scope_vpcs_defined == true
    input.server_assets_defined == true
}

# ---------------------------
# Validate Effective Firewall Policy
# ---------------------------
effective_firewall_policy_verified if {
    input.effective_firewall_rules_available == true
    input.firewall_policy_scope_verified == true
    input.firewall_rule_direction_available == true
    input.firewall_rule_action_available == true
    input.firewall_rule_priority_available == true
    input.firewall_rule_targets_available == true
    input.firewall_rule_match_criteria_available == true
}

# ---------------------------
# Validate Default-Deny Inbound Posture
# ---------------------------
default_deny_inbound_verified if {
    input.default_deny_inbound_enabled == true
    input.scoped_allow_rules_defined == true
    input.broad_inbound_allow_detected == false
}

# ---------------------------
# Validate High-Risk Firewall Logging
# ---------------------------
high_risk_logging_verified if {
    input.high_risk_rule_logging_enabled == true
    input.sample_firewall_log_available == true
    input.sample_log_timestamp != ""
    input.sample_log_rule_name != ""
    input.sample_log_action != ""
}

# ---------------------------
# Validate Cloud Armor Where Applicable
# ---------------------------
cloud_armor_verified if {
    input.cloud_armor_in_scope == false
}

cloud_armor_verified if {
    input.cloud_armor_in_scope == true
    input.cloud_armor_policy_configured == true
    input.cloud_armor_load_balancer_attachment_verified == true
}

# ---------------------------
# Validate Host Firewall Treatment
# ---------------------------
host_firewall_treatment_verified if {
    input.host_firewall_in_scope == false
    input.host_firewall_scope_statement_available == true
}

host_firewall_treatment_verified if {
    input.host_firewall_in_scope == true
    input.host_firewall_policy_configured == true
    input.host_firewall_management_verified == true
    input.host_firewall_compliance_available == true
}

# ---------------------------
# Validate Firewall Review
# ---------------------------
firewall_review_verified if {
    input.periodic_firewall_review_enabled == true
    input.firewall_review_record_available == true
    input.firewall_review_date != ""
    input.firewall_review_owner != ""
}

# ---------------------------
# Validate Change Governance
# ---------------------------
firewall_change_governance_verified if {
    input.firewall_change_governance_enabled == true
    input.firewall_change_approval_required == true
    input.firewall_change_history_available == true
}

# ---------------------------
# Result Output
# ---------------------------
result := output if {

    firewall_policies := get_array(input, "firewall_policies")
    firewall_rules := get_array(input, "firewall_rules")
    high_risk_rules := get_array(input, "high_risk_firewall_rules")
    review_records := get_array(input, "firewall_review_records")

    output := {
        "compliant": compliant,
        "message": generate_message,
        "affected_resources": firewall_rules,
        "details": {
            "server_firewall_process_defined": input.server_firewall_process_defined,
            "server_firewall_scope": input.server_firewall_scope,
            "in_scope_vpcs_defined": input.in_scope_vpcs_defined,
            "server_assets_defined": input.server_assets_defined,
            "effective_firewall_rules_available": input.effective_firewall_rules_available,
            "firewall_policy_scope_verified": input.firewall_policy_scope_verified,
            "default_deny_inbound_enabled": input.default_deny_inbound_enabled,
            "scoped_allow_rules_defined": input.scoped_allow_rules_defined,
            "broad_inbound_allow_detected": input.broad_inbound_allow_detected,
            "high_risk_rule_logging_enabled": input.high_risk_rule_logging_enabled,
            "sample_firewall_log_available": input.sample_firewall_log_available,
            "cloud_armor_in_scope": input.cloud_armor_in_scope,
            "cloud_armor_policy_configured": input.cloud_armor_policy_configured,
            "cloud_armor_load_balancer_attachment_verified": input.cloud_armor_load_balancer_attachment_verified,
            "host_firewall_in_scope": input.host_firewall_in_scope,
            "host_firewall_policy_configured": input.host_firewall_policy_configured,
            "host_firewall_management_verified": input.host_firewall_management_verified,
            "host_firewall_compliance_available": input.host_firewall_compliance_available,
            "firewall_review_record_available": input.firewall_review_record_available,
            "firewall_review_date": input.firewall_review_date,
            "firewall_review_owner": input.firewall_review_owner,
            "firewall_policy_count": count(firewall_policies),
            "firewall_rule_count": count(firewall_rules),
            "high_risk_rule_count": count(high_risk_rules),
            "review_record_count": count(review_records),
            "requires_sample_evidence": true
        }
    }
}

# ---------------------------
# Message Logic
# ---------------------------
generate_message := msg if {
    not input.server_firewall_process_defined
    msg := "FAIL: Server firewall control process is not defined"
}

generate_message := msg if {
    input.server_firewall_process_defined
    not input.server_firewall_scope_defined
    msg := "INCONCLUSIVE: Server firewall scope and in-scope VPC coverage cannot be verified"
}

generate_message := msg if {
    input.server_firewall_scope_defined
    not effective_firewall_policy_verified
    msg := "INCONCLUSIVE: Effective firewall rules or policy scope evidence is incomplete"
}

generate_message := msg if {
    effective_firewall_policy_verified
    not default_deny_inbound_verified
    msg := "FAIL: Default-deny inbound posture is not established or broad inbound exposure exists"
}

generate_message := msg if {
    default_deny_inbound_verified
    not high_risk_logging_verified
    msg := "FAIL: Logging for high-risk or internet-facing firewall rules is not sufficiently evidenced"
}

generate_message := msg if {
    high_risk_logging_verified
    not cloud_armor_verified
    msg := "FAIL: Cloud Armor protection is not configured for an applicable exposed HTTP(S) workload"
}

generate_message := msg if {
    cloud_armor_verified
    not host_firewall_treatment_verified
    msg := "FAIL: Host firewall treatment is unclear or host-level firewall enforcement is not evidenced"
}

generate_message := msg if {
    host_firewall_treatment_verified
    not firewall_change_governance_verified
    msg := "FAIL: Firewall rule changes cannot be traced to an approval workflow"
}

generate_message := msg if {
    firewall_change_governance_verified
    not firewall_review_verified
    msg := "FAIL: Periodic firewall rule review or recertification evidence is missing"
}

generate_message := msg if {
    firewall_review_verified
    compliant
    msg := "PASS: Server firewall controls are implemented with default-deny inbound protection, scoped exceptions, high-risk logging, governed changes, and periodic review"
}

# ---------------------------
# Helper Functions
# ---------------------------
get_array(obj, key) := value if {
    value := obj[key]
} else := []
