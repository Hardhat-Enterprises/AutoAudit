# METADATA
# title: Use DNS Filtering Services (GCP)
# description: |
#   Organisations must use DNS filtering services on all end-user devices, including remote and
#   on-premises assets, to block access to known malicious domains. This is enforced via Cloud DNS
#   response policies for VPC-resolved traffic, alongside DNS query logging for visibility. For roaming
#   endpoints that do not resolve through GCP DNS, an enterprise DNS filtering/SWG solution outside
#   native GCP is required to cover off-network devices.
#   Policy scope (VPC/network) and coverage must be confirmed, and a time-stamped DNS query log or report
#   showing blocked resolution attempts must be provided as evidence the policy is actively enforced.
# related_resources:
# - ref: https://cloud.google.com/dns/docs/policies
#   description: Cloud DNS Response Policy Documentation
# - ref: https://cloud.google.com/dns/docs/monitoring
#   description: Cloud DNS Query Logging Documentation
# custom:
#   control_id: CIS-9.2
#   framework: cis
#   benchmark: gcp-foundations
#   version: v2.0.0
#   severity: medium
#   service: Cloud DNS
#   requires_permissions:
#   - dns.policies.list
#   - dns.policies.get
#   - logging.logEntries.list

package cis.gcp_foundations.v2_0_0.control_9_2

import rego.v1

# Default message
default result := {
    "compliant": false,
    "message": "Evaluation failed: insufficient data to verify DNS filtering is configured and enforced.",
    "details": {},
}

default compliant := false

# ---------------------------
# Compliance Logic
# ---------------------------
compliant if {
    dns_filtering_configured
    dns_filtering_scope_defined
    dns_blocking_evidence_recent
    roaming_coverage_addressed
}

#dns filtering configuration view must show denied domains or reputation categories, 
#as this ensures protection - the policy must exist and contain enforceable deny rules,
dns_filtering_configured if {
    input.dns_response_policy_name != ""
    input.denied_domains_configured == true
}

#networks must use the filtered resolver path to confirm that its protecting real traffic
dns_filtering_scope_defined if {
    input.dns_policy_scope_type != ""
    input.dns_policy_scope_identifier != ""
}

#there should be a time stamped log of blocked resolution attempts - should be a recent/dated log
#a policy with no blocked-query evidence can't be confirmed as operating
dns_blocking_evidence_recent if {
    input.dns_log_sample_date != ""
    input.dns_log_within_review_window == true
}

#checks whether off-network devices are covered by a seperate enterprise DNS filtering solution
roaming_coverage_addressed if {
    input.roaming_dns_filtering_provider != ""
    input.roaming_coverage_confirmed == true
}

# ---------------------------
# Result Output
# ---------------------------
result := output if {
    blocked_dns_queries := get_array(input, "blocked_dns_queries")

    output := {
        "compliant": compliant,
        "message": generate_message,
        "affected_resources": blocked_dns_queries,
        "details": {
            "dns_response_policy_name": input.dns_response_policy_name,
            "denied_domains_configured": input.denied_domains_configured,
            "dns_policy_scope_type": input.dns_policy_scope_type,
            "dns_policy_scope_identifier": input.dns_policy_scope_identifier,
            "dns_log_sample_date": input.dns_log_sample_date,
            "dns_log_within_review_window": input.dns_log_within_review_window,
            "roaming_dns_filtering_provider": input.roaming_dns_filtering_provider,
            "roaming_coverage_confirmed": input.roaming_coverage_confirmed,
            "blocked_dns_queries_count": count(blocked_dns_queries),
            "requires_example_evidence": true,
        }
    }
}

# ---------------------------
# Message Logic
# ---------------------------
generate_message := msg if {
    not dns_filtering_configured
    msg := "FAIL: No DNS filtering policy is configured, or it contains no enforceable deny rules."
}

generate_message := msg if {
    dns_filtering_configured
    not dns_filtering_scope_defined
    msg := "INCONCLUSIVE: No VPC or network scope is defined for the DNS filtering policy, so it cannot be confirmed as protecting any real traffic."
}

generate_message := msg if {
    dns_filtering_configured
    dns_filtering_scope_defined
    not dns_blocking_evidence_recent
    msg := "INCONCLUSIVE: No recent, time-stamped DNS query log was found showing blocked resolution attempts."
}

generate_message := msg if {
    dns_filtering_configured
    dns_filtering_scope_defined
    dns_blocking_evidence_recent
    not roaming_coverage_addressed
    msg := "FAIL: Off-network devices are not covered by a separate enterprise DNS filtering solution."
}

generate_message := msg if {
    compliant
    msg := "PASS: DNS filtering is configured, attached to the relevant resolution paths, and logs demonstrate real blocked queries within the stated review window."
}

# ---------------------------
# Helper Functions
# ---------------------------
get_array(obj, key) := value if {
    value := obj[key]
} else := []
