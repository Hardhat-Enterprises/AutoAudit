# METADATA
# title: Collect URL Request Audit Logs (GCP)
# description: |
#   Organisations must collect URL request audit logs on enterprise assets, where appropriate and
#   supported.
#   HTTP and HTTPS request telemetry should be captured at common control points such as External or
#   Internal HTTP(S) Load Balancers, Cloud Armor, and API Gateway or Cloud Endpoints. Request logs must
#   include URL path, status, user agent, and source IP where available, and be routed to the central
#   logging destination.
# related_resources:
# - ref: https://cloud.google.com/load-balancing/docs/https/https-logging-monitoring
#   description: HTTP(S) Load Balancer Logging Documentation
# - ref: https://cloud.google.com/armor/docs/logging
#   description: Cloud Armor Logging Documentation
# custom:
#   control_id: CIS-8.7
#   framework: cis
#   benchmark: gcp-foundations
#   version: v2.0.0
#   severity: low
#   service: Cloud Load Balancing / Cloud Armor / API Gateway
#   requires_permissions:
#   - compute.backendServices.list
#   - logging.logEntries.list
#   - apigateway.gateways.list

package cis.gcp_foundations.v2_0_0.control_8_7

import rego.v1

# Default result
default result := {
	"compliant": false,
	"message": "Evaluation failed: insufficient data to verify URL request audit logging",
	"details": {},
}

default compliant := false

# ---------------------------
# Compliance Logic
# ---------------------------
compliant if {
	entry_points_defined
	all_entry_points_logging_enabled
	has_sample_request_log_entry
	input.central_routing_confirmed == true
}

# At least one public-facing entry point must be documented - without a defined
# list, coverage can't be confirmed as complete rather than partial or unknown
entry_points_defined if {
	count(input.entry_points) > 0
}

# Every documented entry point must have request logging enabled -
# one unlogged entry point is a coverage gap, not a pass
all_entry_points_logging_enabled if {
	every ep in input.entry_points {
		ep.request_logging_enabled == true
	}
}

# At least one real request log entry must show URL-level detail -
# proving request logging is producing usable data, not just switched on
has_sample_request_log_entry if {
	some entry in input.sample_log_entries
	entry.request_url != ""
	entry.status != ""
	entry.timestamp != ""
}

# ---------------------------
# Result Output
# ---------------------------
result := output if {
	entry_points := get_array(input, "entry_points")
	sample_log_entries := get_array(input, "sample_log_entries")

	output := {
		"compliant": compliant,
		"message": generate_message,
		"affected_resources": entry_points,
		"details": {
			"entry_point_count": count(entry_points),
			"sample_log_entry_count": count(sample_log_entries),
			"central_routing_confirmed": input.central_routing_confirmed,
			"requires_example_evidence": true,
		},
	}
}

# ---------------------------
# Message Logic
# ---------------------------
generate_message := msg if {
	not entry_points_defined
	msg := "INCONCLUSIVE: In-scope public entry points have not been documented"
}

generate_message := msg if {
	entry_points_defined
	not all_entry_points_logging_enabled
	msg := "FAIL: One or more in-scope entry points do not have request logging enabled"
}

generate_message := msg if {
	all_entry_points_logging_enabled
	not has_sample_request_log_entry
	msg := "INCONCLUSIVE: No sample request log entry found showing URL-level detail"
}

generate_message := msg if {
	has_sample_request_log_entry
	not input.central_routing_confirmed
	msg := "FAIL: URL request logs are not confirmed as routed to the central logging destination"
}

generate_message := msg if {
	compliant
	msg := "PASS: Request logging is enabled across in-scope entry points, sample logs show URL-level detail, and logs are routed centrally"
}

# ---------------------------
# Helper Functions
# ---------------------------
get_array(obj, key) := value if {
	value := obj[key]
} else := []
