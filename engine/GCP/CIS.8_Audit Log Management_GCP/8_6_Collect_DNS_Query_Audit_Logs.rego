# METADATA
# title: Collect DNS Query Audit Logs (GCP)
# description: |
#   Organisations must collect DNS query audit logs on enterprise assets, where appropriate and supported.
#   Cloud DNS query logging should be enabled where Cloud DNS is used for VPC resolution or authoritative
#   zones in scope, with logs flowing into Cloud Logging and routed to the central logging destination.
#   Where DNS is handled by a different resolver, the alternative source and how it is captured must be
#   documented instead.
# related_resources:
# - ref: https://cloud.google.com/dns/docs/monitoring
#   description: Cloud DNS Query Logging Documentation
# custom:
#   control_id: CIS-8.6
#   framework: cis
#   benchmark: gcp-foundations
#   version: v2.0.0
#   severity: low
#   service: Cloud DNS / Cloud Logging
#   requires_permissions:
#   - dns.policies.list
#   - dns.managedZones.list
#   - logging.logEntries.list

package cis.gcp_foundations.v2_0_0.control_8_6

import rego.v1

# Default result
default result := {
	"compliant": false,
	"message": "Evaluation failed: insufficient data to verify DNS query audit logging",
	"details": {},
}

default compliant := false

# ---------------------------
# Compliance Logic
# ---------------------------
# Path 1: DNS is provided via Cloud DNS - logging, scope, sample evidence,
# and central routing all need to be confirmed
compliant if {
	input.dns_provider == "cloud_dns"
	cloud_dns_logging_confirmed
	has_sample_dns_log_entry
	input.central_routing_confirmed == true
}

# Path 2: DNS is provided elsewhere - an alternative source and its own
# logging evidence must be documented instead
compliant if {
	input.dns_provider == "other"
	alternative_dns_documented
}

# Cloud DNS logging must be enabled and applied to a defined policy, zone, or
# network scope -- enabled with no defined scope can't be confirmed as coverage
cloud_dns_logging_confirmed if {
	input.cloud_dns_logging_enabled == true
	input.dns_logging_scope != ""
}

# At least one real DNS query log entry must be present with the key fields
# needed to confirm query activity is actually being captured
has_sample_dns_log_entry if {
	some entry in input.sample_dns_log_entries
	entry.query_name != ""
	entry.query_type != ""
	entry.response_code != ""
	entry.timestamp != ""
}

# When DNS is resolved outside Cloud DNS, the alternative source and its
# equivalent logging evidence must both be documented
alternative_dns_documented if {
	input.alternative_dns_source != ""
	input.alternative_dns_evidence != ""
}

# ---------------------------
# Result Output
# ---------------------------
result := output if {
	sample_dns_log_entries := get_array(input, "sample_dns_log_entries")

	output := {
		"compliant": compliant,
		"message": generate_message,
		"affected_resources": sample_dns_log_entries,
		"details": {
			"dns_provider": input.dns_provider,
			"cloud_dns_logging_enabled": input.cloud_dns_logging_enabled,
			"dns_logging_scope": input.dns_logging_scope,
			"sample_dns_log_entry_count": count(sample_dns_log_entries),
			"central_routing_confirmed": input.central_routing_confirmed,
			"alternative_dns_source": input.alternative_dns_source,
			"requires_example_evidence": true,
		},
	}
}

# ---------------------------
# Message Logic
# ---------------------------
generate_message := msg if {
	input.dns_provider == ""
	msg := "INCONCLUSIVE: DNS provider or resolution source has not been documented"
}

generate_message := msg if {
	input.dns_provider == "cloud_dns"
	not cloud_dns_logging_confirmed
	msg := "FAIL: Cloud DNS query logging is not enabled, or its scope is not defined"
}

generate_message := msg if {
	input.dns_provider == "cloud_dns"
	cloud_dns_logging_confirmed
	not has_sample_dns_log_entry
	msg := "INCONCLUSIVE: No sample DNS query log entry found to confirm logging activity"
}

generate_message := msg if {
	input.dns_provider == "cloud_dns"
	has_sample_dns_log_entry
	not input.central_routing_confirmed
	msg := "FAIL: DNS query logs are not confirmed as routed to the central logging destination"
}

generate_message := msg if {
	input.dns_provider == "other"
	not alternative_dns_documented
	msg := "INCONCLUSIVE: DNS is resolved outside Cloud DNS but no alternative source or evidence has been documented"
}

generate_message := msg if {
	compliant
	msg := "PASS: DNS query logging is enabled and evidenced for the applicable resolver, with logs routed to the central destination"
}

# ---------------------------
# Helper Functions
# ---------------------------
get_array(obj, key) := value if {
	value := obj[key]
} else := []
