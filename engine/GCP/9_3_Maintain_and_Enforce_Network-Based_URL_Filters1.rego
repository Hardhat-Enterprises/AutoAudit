# METADATA
# title: Maintain and Enforce Network-Based URL Filters (GCP)
# description: |
#   Organisations must enforce and update network-based URL filters to limit enterprise assets from
#   connecting to potentially malicious or unapproved websites, using category-based filtering,
#   reputation-based filtering, or block lists. Filters must be enforced for all enterprise assets.
#   This is implemented via Secure Web Proxy / Secure Web Gateway patterns for outbound web filtering,
#   and Cloud Armor policy controls for inbound web properties, with logging via load balancer and
#   Cloud Armor logs for block visibility.
#   Policy scope (users/devices/networks and protected web properties) must be confirmed, a time-stamped
#   log sample showing blocked URL requests must be provided, and a recent rule change record must
#   demonstrate the filters are actively maintained and updated over time.
# related_resources:
# - ref: https://cloud.google.com/armor/docs/security-policy-overview
#   description: Cloud Armor Security Policy Documentation
# - ref: https://cloud.google.com/secure-web-proxy/docs/overview
#   description: Secure Web Proxy Documentation
# custom:
#   control_id: CIS-9.3
#   framework: cis
#   benchmark: gcp-foundations
#   version: v2.0.0
#   severity: medium
#   service: Cloud Armor / Secure Web Proxy
#   requires_permissions:
#   - compute.securityPolicies.list
#   - compute.securityPolicies.get
#   - networksecurity.gatewaySecurityPolicies.list
#   - logging.logEntries.list

package cis.gcp_foundations.v2_0_0.control_9_3

import rego.v1

#Default result
default result := {
	"compliant": false,
	"message": "Evaluation failed: insufficient data to verify network-based URL filters.",
	"details": {},
}

default compliant := false

# ---------------------------
# Compliance Logic
# ---------------------------
compliant if {
	url_filtering_configured
	coverage_evidence_defined
	log_sample_shown
	rule_maintenance_evidenced
}

#a URL filtering policy with no category oe explicit allow/deny lists doesnt provide any enforcement -
#the policy must exist and contain real rules 
url_filtering_configured if {
	input.url_filter_policy_name != ""
	input.url_filter_rules_configured == true
}

#a filtering policy that isnt confirmed as forcing users/devices/networks through it, and protecting
#specific web properties cant be relied on as enforced
coverage_evidence_defined if {
	input.url_filter_scope_type != ""
	input.url_filter_scope_identifier != ""
}

#the policy must be shown blocking real requests via a recent and dated log -
#a policy without blocked-request evidence cant be confirmed as operating
log_sample_shown if {
	input.url_log_sample_date != ""
	input.url_log_within_review_window == true
}

#the safeguard requires filters to be enforced and updated over time - a static rule set without
#maintenance history doesnt meet the update requirement
rule_maintenance_evidenced if {
	input.rule_change_record_date != ""
	input.rule_change_reference != ""
}

# ---------------------------
# Result Output
# ---------------------------
result := output if {
	blocked_url_requests := get_array(input, "blocked_url_requests")

	output := {
		"compliant": compliant,
		"message": generate_message,
		"affected_resources": blocked_url_requests,
		"details": {
			"url_filter_policy_name": input.url_filter_policy_name,
			"url_filter_rules_configured": input.url_filter_rules_configured,
			"url_filter_scope_type": input.url_filter_scope_type,
			"url_filter_scope_identifier": input.url_filter_scope_identifier,
			"url_log_sample_date": input.url_log_sample_date,
			"url_log_within_review_window": input.url_log_within_review_window,
			"rule_change_record_date": input.rule_change_record_date,
			"rule_change_reference": input.rule_change_reference,
			"blocked_url_requests_count": count(blocked_url_requests),
			"requires_example_evidence": true,
		}
	}
}

# ---------------------------
# Message Logic
# ---------------------------
generate_message := msg if {
	not url_filtering_configured
	msg := "FAIL: No URL filtering policy found."
}

generate_message := msg if {
	url_filtering_configured
	not coverage_evidence_defined
	msg := "INCONCLUSIVE: Filtering policy isn't confirmed as forcing users/networks/devices through it, so it cannot be confirmed as protectiing web policies."
}

generate_message := msg if {
	url_filtering_configured
	coverage_evidence_defined
	not log_sample_shown
	msg := "INCONCLUSIVE: Policy does not show blocked-request evidence, so it cannot be confirmed as operating."
}

generate_message := msg if {
	url_filtering_configured
	coverage_evidence_defined
	log_sample_shown
	not rule_maintenance_evidenced
	msg := "INCONCLUSIVE: No rule change history or reference was found showing filters are actively maintained and updated over time."
}

generate_message := msg if {
	compliant
	msg := "PASS: URL filtering rules are explicit and configured, coverage confirms enforcement for the defined population, logs show real blocked requests, and rule change history confirms ongoing maintenance."
}

# ---------------------------
# Helper Functions
# ---------------------------
get_array(obj, key) := value if {
	value := obj[key]
} else := []