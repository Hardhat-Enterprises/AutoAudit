# METADATA
# title: Configure Trusted DNS Servers on Enterprise Assets (GCP)
# description: |
#   Enterprise network workloads must use trusted and enterprise-controlled
#   DNS resolvers for name resolution.
#
#   Trusted DNS is achieved when workloads resolve names through a
#   controlled path that the enterprise can monitor and enforce.
#
#   Google Cloud implementation uses:
#   - Cloud DNS private zones for controlled internal name resolution
#   - Cloud DNS policies to standardize resolver behavior
#   - DNS forwarding where required
#   - DNS query logging to Cloud Logging
#   - VPC firewall rules and egress controls to prevent workloads from
#     bypassing approved DNS resolvers
#   - DNS monitoring and detection mechanisms to identify suspicious
#     domain resolution
#
#   The control verifies:
#   - Approved DNS resolvers are defined
#   - DNS policies are configured and attached to the correct scope
#   - Private DNS zones are configured where applicable
#   - Forwarding behavior is defined where applicable
#   - DNS query logging is enabled
#   - DNS logs contain sufficient evidence for monitoring
#   - DNS logs are retained
#   - Direct DNS access to arbitrary external resolvers is prevented
#   - DNS egress is restricted to approved resolvers
#   - Suspicious DNS activity is periodically reviewed or detected
#
#   Cloud DNS provides the primary controlled DNS mechanism. Firewall
#   controls are treated as an enforcement layer preventing workloads
#   from bypassing the approved DNS resolution path.
#
# related_resources:
# - ref: https://cloud.google.com/dns/docs/overview
#   description: Cloud DNS Documentation
# - ref: https://cloud.google.com/dns/docs/policies/overview
#   description: Cloud DNS Policies Documentation
# - ref: https://cloud.google.com/dns/docs/zones
#   description: Cloud DNS Zones Documentation
# - ref: https://cloud.google.com/logging/docs
#   description: Cloud Logging Documentation
# - ref: https://cloud.google.com/firewall/docs
#   description: Google Cloud Firewall Documentation
#
# custom:
#   control_id: CIS-4.9
#   framework: cis
#   benchmark: gcp-foundations
#   version: v2.0.0
#   safeguard: 4.9
#   severity: medium
#   service: Cloud DNS / VPC Firewall / Cloud Logging
#   asset_type: Devices
#   implementation_group: 2
#   requires_permissions:
#   - dns.policies.list
#   - dns.policies.get
#   - dns.managedZones.list
#   - dns.managedZones.get
#   - compute.networks.list
#   - compute.firewalls.list
#   - logging.viewer
#   - logging.logEntries.list

package cis.gcp_foundations.v2_0_0.control_4_9

import rego.v1

# ---------------------------
# Default Result
# ---------------------------
default compliant := false

default result := {
    "compliant": false,
    "message": "Evaluation failed: insufficient trusted DNS evidence",
    "details": {}
}

# ---------------------------
# Compliance Logic
# ---------------------------
compliant if {
    trusted_dns_process_defined
    trusted_dns_scope_defined
    approved_resolvers_verified
    dns_policy_verified
    dns_logging_verified
    dns_bypass_prevention_verified
    dns_monitoring_verified
}

# ---------------------------
# Validate DNS Process
# ---------------------------
trusted_dns_process_defined if {
    input.trusted_dns_process_defined == true
    input.approved_dns_standard_defined == true
    input.approved_dns_resolvers_defined == true
}

# ---------------------------
# Validate DNS Scope
# ---------------------------
trusted_dns_scope_defined if {
    input.trusted_dns_scope != ""
    input.in_scope_vpcs_defined == true
    input.in_scope_workloads_defined == true
}

# ---------------------------
# Validate Approved DNS Resolvers
# ---------------------------
approved_resolvers_verified if {
    input.approved_resolvers_defined == true
    input.approved_resolver_list_available == true
    input.approved_resolver_list_count > 0
}

# ---------------------------
# Validate Cloud DNS Policy
# ---------------------------
dns_policy_verified if {
    input.cloud_dns_policy_configured == true
    input.dns_policy_scope_defined == true
    input.dns_policy_attachment_verified == true
    input.dns_resolution_path_defined == true
}

# ---------------------------
# Validate Private DNS Zones
# ---------------------------
private_dns_zone_verified if {
    input.private_dns_zones_in_scope == false
}

private_dns_zone_verified if {
    input.private_dns_zones_in_scope == true
    input.private_dns_zone_configured == true
    input.private_dns_zone_scope_verified == true
}

# ---------------------------
# Validate DNS Forwarding
# ---------------------------
dns_forwarding_verified if {
    input.dns_forwarding_in_scope == false
}

dns_forwarding_verified if {
    input.dns_forwarding_in_scope == true
    input.dns_forwarding_configured == true
    input.dns_forwarding_targets_defined == true
    input.dns_forwarding_targets_approved == true
}

# ---------------------------
# Validate DNS Logging
# ---------------------------
dns_logging_verified if {
    input.dns_query_logging_enabled == true
    input.dns_log_sink_or_destination_defined == true
    input.sample_dns_log_available == true
    input.sample_dns_log_timestamp != ""
}

# ---------------------------
# Validate DNS Log Retention
# ---------------------------
dns_retention_verified if {
    input.dns_log_retention_configured == true
    input.dns_log_retention_period_days > 0
}

# ---------------------------
# Validate DNS Bypass Prevention
# ---------------------------
dns_bypass_prevention_verified if {
    input.dns_bypass_prevention_enabled == true
    input.arbitrary_external_dns_allowed == false
    input.direct_dns_egress_restricted == true
    input.approved_dns_egress_rules_defined == true
}

# ---------------------------
# Validate DNS Monitoring
# ---------------------------
dns_monitoring_verified if {
    input.dns_monitoring_enabled == true
    input.dns_review_or_detection_process_defined == true
    input.suspicious_dns_detection_evidence_available == true
}

# ---------------------------
# Validate DNS Review
# ---------------------------
dns_review_verified if {
    input.dns_review_record_available == true
    input.dns_review_date != ""
    input.dns_review_owner != ""
}

# ---------------------------
# Result Output
# ---------------------------
result := output if {

    dns_policies := get_array(input, "dns_policies")
    private_zones := get_array(input, "private_dns_zones")
    approved_resolvers := get_array(input, "approved_dns_resolvers")
    firewall_rules := get_array(input, "dns_egress_firewall_rules")
    dns_logs := get_array(input, "dns_query_logs")
    detections := get_array(input, "dns_detections")

    output := {
        "compliant": compliant,
        "message": generate_message,
        "affected_resources": approved_resolvers,

        "details": {
            "trusted_dns_process_defined":
                input.trusted_dns_process_defined,

            "approved_dns_standard_defined":
                input.approved_dns_standard_defined,

            "trusted_dns_scope":
                input.trusted_dns_scope,

            "in_scope_vpcs_defined":
                input.in_scope_vpcs_defined,

            "in_scope_workloads_defined":
                input.in_scope_workloads_defined,

            "approved_resolvers_defined":
                input.approved_resolvers_defined,

            "approved_resolver_list_count":
                input.approved_resolver_list_count,

            "cloud_dns_policy_configured":
                input.cloud_dns_policy_configured,

            "dns_policy_scope_defined":
                input.dns_policy_scope_defined,

            "dns_policy_attachment_verified":
                input.dns_policy_attachment_verified,

            "dns_resolution_path_defined":
                input.dns_resolution_path_defined,

            "private_dns_zones_in_scope":
                input.private_dns_zones_in_scope,

            "private_dns_zone_configured":
                input.private_dns_zone_configured,

            "private_dns_zone_scope_verified":
                input.private_dns_zone_scope_verified,

            "dns_forwarding_in_scope":
                input.dns_forwarding_in_scope,

            "dns_forwarding_configured":
                input.dns_forwarding_configured,

            "dns_forwarding_targets_defined":
                input.dns_forwarding_targets_defined,

            "dns_forwarding_targets_approved":
                input.dns_forwarding_targets_approved,

            "dns_query_logging_enabled":
                input.dns_query_logging_enabled,

            "dns_log_sink_or_destination_defined":
                input.dns_log_sink_or_destination_defined,

            "sample_dns_log_available":
                input.sample_dns_log_available,

            "sample_dns_log_timestamp":
                input.sample_dns_log_timestamp,

            "dns_log_retention_configured":
                input.dns_log_retention_configured,

            "dns_log_retention_period_days":
                input.dns_log_retention_period_days,

            "dns_bypass_prevention_enabled":
                input.dns_bypass_prevention_enabled,

            "arbitrary_external_dns_allowed":
                input.arbitrary_external_dns_allowed,

            "direct_dns_egress_restricted":
                input.direct_dns_egress_restricted,

            "approved_dns_egress_rules_defined":
                input.approved_dns_egress_rules_defined,

            "dns_monitoring_enabled":
                input.dns_monitoring_enabled,

            "dns_review_or_detection_process_defined":
                input.dns_review_or_detection_process_defined,

            "suspicious_dns_detection_evidence_available":
                input.suspicious_dns_detection_evidence_available,

            "dns_review_record_available":
                input.dns_review_record_available,

            "dns_review_date":
                input.dns_review_date,

            "dns_review_owner":
                input.dns_review_owner,

            "dns_policy_count":
                count(dns_policies),

            "private_zone_count":
                count(private_zones),

            "approved_resolver_count":
                count(approved_resolvers),

            "dns_egress_firewall_rule_count":
                count(firewall_rules),

            "dns_log_count":
                count(dns_logs),

            "dns_detection_count":
                count(detections),

            "requires_sample_evidence":
                true
        }
    }
}

# ---------------------------
# Message Logic
# ---------------------------

generate_message := msg if {
    not trusted_dns_process_defined
    msg := "FAIL: Trusted DNS standard or approved resolver process is not defined"
}

generate_message := msg if {
    trusted_dns_process_defined
    not trusted_dns_scope_defined
    msg := "INCONCLUSIVE: DNS policy scope and affected VPC workloads cannot be verified"
}

generate_message := msg if {
    trusted_dns_scope_defined
    not approved_resolvers_verified
    msg := "FAIL: Approved DNS resolvers are not defined or documented"
}

generate_message := msg if {
    approved_resolvers_verified
    not dns_policy_verified
    msg := "INCONCLUSIVE: Cloud DNS policy or resolver attachment scope cannot be verified"
}

generate_message := msg if {
    dns_policy_verified
    not private_dns_zone_verified
    msg := "INCONCLUSIVE: Required Cloud DNS private zone configuration cannot be verified"
}

generate_message := msg if {
    private_dns_zone_verified
    not dns_forwarding_verified
    msg := "FAIL: DNS forwarding targets are not defined or are not approved"
}

generate_message := msg if {
    dns_forwarding_verified
    not dns_logging_verified
    msg := "FAIL: DNS query logging is disabled or sample DNS query evidence is unavailable"
}

generate_message := msg if {
    dns_logging_verified
    not dns_retention_verified
    msg := "FAIL: DNS log retention is not configured or cannot be demonstrated"
}

generate_message := msg if {
    dns_retention_verified
    not dns_bypass_prevention_verified
    msg := "FAIL: Workloads can bypass approved DNS resolvers or direct DNS egress is not sufficiently restricted"
}

generate_message := msg if {
    dns_bypass_prevention_verified
    not dns_monitoring_verified
    msg := "FAIL: DNS monitoring or suspicious-domain detection is not sufficiently evidenced"
}

generate_message := msg if {
    dns_monitoring_verified
    not dns_review_verified
    msg := "INCONCLUSIVE: DNS monitoring exists but periodic review or detection evidence is missing"
}

generate_message := msg if {
    dns_review_verified
    compliant
    msg := "PASS: Trusted DNS resolvers are defined and enforced, DNS queries are logged and retained, resolver bypass is restricted, and DNS activity is monitored"
}

# ---------------------------
# Helper Functions
# ---------------------------

get_array(obj, key) := value if {
    value := obj[key]
} else := []
