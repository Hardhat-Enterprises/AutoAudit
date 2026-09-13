# METADATA
# title: Collect Service Provider Logs (GCP)
# description: |
#   Organisations must collect service provider logs, where supported, including authentication and
#   authorization events, data creation and disposal events, and user management events.
#   Provider-side telemetry such as Access Transparency logs should be collected where available, with
#   provider-originated admin and security events retained alongside tenant audit logs and routed to the
#   same central destination. Where a feature is not available in the edition in use, that limitation and
#   the alternative monitoring approach must be documented instead.
# related_resources:
# - ref: https://cloud.google.com/assured-workloads/access-transparency/docs/overview
#   description: Access Transparency Documentation
# custom:
#   control_id: CIS-8.12
#   framework: cis
#   benchmark: gcp-foundations
#   version: v2.0.0
#   severity: low
#   service: Access Transparency / Cloud Logging
#   requires_permissions:
#   - logging.logEntries.list
#   - resourcemanager.organizations.get

package cis.gcp_foundations.v2_0_0.control_8_12

import rego.v1

# Default result
default result := {
	"compliant": false,
	"message": "Evaluation failed: insufficient data to verify service provider log collection",
	"details": {},
}

default compliant := false

# ---------------------------
# Compliance Logic
# ---------------------------
# Path 1: Provider logging is supported in this environment - enablement, scope,
# sample evidence, and central routing all need to be confirmed
compliant if {
	input.provider_log_support_status == "supported"
	input.provider_log_feature_enabled == true
	input.provider_log_scope != ""
	has_sample_provider_log_entry
	input.central_routing_confirmed == true
}

# Path 2: Provider logging is not supported in this edition - the limitation and
# an alternative monitoring approach must be documented instead
compliant if {
	input.provider_log_support_status == "not_supported"
	alternative_monitoring_documented
}

# At least one real provider-originated log entry must be present, confirming
# provider events are actually being captured, not just entitled
has_sample_provider_log_entry if {
	some entry in input.sample_provider_log_entries
	entry.event_type != ""
	entry.timestamp != ""
	entry.affected_resource != ""
}

# When the feature isn't supported, both the edition limitation and the
# alternative monitoring approach must be explicitly documented
alternative_monitoring_documented if {
	input.edition_statement != ""
	input.alternative_monitoring_description != ""
}

# ---------------------------
# Result Output
# ---------------------------
result := output if {
	sample_provider_log_entries := get_array(input, "sample_provider_log_entries")

	output := {
		"compliant": compliant,
		"message": generate_message,
		"affected_resources": sample_provider_log_entries,
		"details": {
			"provider_log_support_status": input.provider_log_support_status,
			"provider_log_feature_enabled": input.provider_log_feature_enabled,
			"provider_log_scope": input.provider_log_scope,
			"sample_provider_log_entry_count": count(sample_provider_log_entries),
			"central_routing_confirmed": input.central_routing_confirmed,
			"edition_statement": input.edition_statement,
			"requires_example_evidence": true,
		},
	}
}

# ---------------------------
# Message Logic
# ---------------------------
generate_message := msg if {
	input.provider_log_support_status == ""
	msg := "INCONCLUSIVE: Provider log feature availability for this environment has not been documented"
}

generate_message := msg if {
	input.provider_log_support_status == "supported"
	not input.provider_log_feature_enabled
	msg := "FAIL: Provider logging is supported for this environment but has not been enabled"
}

generate_message := msg if {
	input.provider_log_support_status == "supported"
	input.provider_log_feature_enabled
	input.provider_log_scope == ""
	msg := "FAIL: Provider logging is enabled but has no defined scope"
}

generate_message := msg if {
	input.provider_log_support_status == "supported"
	input.provider_log_feature_enabled
	input.provider_log_scope != ""
	not has_sample_provider_log_entry
	msg := "INCONCLUSIVE: No sample provider-originated log entry found to confirm events are being captured"
}

generate_message := msg if {
	input.provider_log_support_status == "supported"
	has_sample_provider_log_entry
	not input.central_routing_confirmed
	msg := "FAIL: Provider logs are not confirmed as routed to the central logging destination"
}

generate_message := msg if {
	input.provider_log_support_status == "not_supported"
	not alternative_monitoring_documented
	msg := "INCONCLUSIVE: Provider logging is not supported in this environment, but no alternative monitoring approach has been documented"
}

generate_message := msg if {
	compliant
	msg := "PASS: Provider logs are enabled and evidenced where supported, or an alternative monitoring approach is documented where not supported"
}

# ---------------------------
# Helper Functions
# ---------------------------
get_array(obj, key) := value if {
	value := obj[key]
} else := []
