# METADATA
# title: Conduct Audit Log Reviews (GCP)
# description: |
#   Organisations must conduct reviews of audit logs to detect anomalies or abnormal events that could
#   indicate a potential threat, on a weekly or more frequent basis.
#   Log review should be operationalised through log-based metrics and alert policies for high-risk
#   events, along with scheduled queries for anomaly checks. A lightweight trail of review outcomes
#   should be kept through tickets or cases so the cadence and response are auditable.
# related_resources:
# - ref: https://cloud.google.com/logging/docs/alerting/log-based-alerts
#   description: Log-Based Alerting Documentation
# - ref: https://cloud.google.com/logging/docs/logs-based-metrics
#   description: Log-Based Metrics Documentation
# custom:
#   control_id: CIS-8.11
#   framework: cis
#   benchmark: gcp-foundations
#   version: v2.0.0
#   severity: medium
#   service: Cloud Logging / Cloud Monitoring
#   requires_permissions:
#   - logging.metrics.list
#   - monitoring.alertPolicies.list
#   - logging.logEntries.list

package cis.gcp_foundations.v2_0_0.control_8_11

import rego.v1

# Default result
default result := {
	"compliant": false,
	"message": "Evaluation failed: insufficient data to verify audit log review process",
	"details": {},
}

default compliant := false

# ---------------------------
# Compliance Logic
# ---------------------------
compliant if {
	has_active_alert_policies
	review_cadence_confirmed
	has_investigation_artefact
}

# Every alert/detection policy in scope must be enabled - an inactive or
# disabled policy provides no actual anomaly detection coverage
has_active_alert_policies if {
	count(input.alert_policies) > 0
	every a in input.alert_policies {
		a.enabled == true
	}
}

# Review cadence evidence must exist and be confirmed as weekly or more frequent -
# the frequency assessment itself is expected to come from the evidence review step
review_cadence_confirmed if {
	count(input.review_cadence_evidence) > 0
	input.review_cadence_weekly_or_better == true
}

# At least one real investigation artefact must link a specific log event to
# triage and follow-up action, proving anomalies are acted on, not just detected
has_investigation_artefact if {
	input.investigation_artefact.ticket_id != ""
	input.investigation_artefact.linked_log_event != ""
}

# ---------------------------
# Result Output
# ---------------------------
result := output if {
	alert_policies := get_array(input, "alert_policies")
	review_cadence_evidence := get_array(input, "review_cadence_evidence")

	output := {
		"compliant": compliant,
		"message": generate_message,
		"affected_resources": alert_policies,
		"details": {
			"alert_policy_count": count(alert_policies),
			"review_cadence_evidence_count": count(review_cadence_evidence),
			"review_cadence_weekly_or_better": input.review_cadence_weekly_or_better,
			"investigation_artefact": input.investigation_artefact,
			"requires_example_evidence": true,
		},
	}
}

# ---------------------------
# Message Logic
# ---------------------------
generate_message := msg if {
	not has_active_alert_policies
	msg := "FAIL: No active alert or detection policies are tied to audit log events"
}

generate_message := msg if {
	has_active_alert_policies
	count(input.review_cadence_evidence) == 0
	msg := "INCONCLUSIVE: No review cadence evidence provided to confirm a weekly or more frequent review cycle"
}

generate_message := msg if {
	has_active_alert_policies
	count(input.review_cadence_evidence) > 0
	not input.review_cadence_weekly_or_better
	msg := "FAIL: Review cadence evidence does not demonstrate a weekly or more frequent review cycle"
}

generate_message := msg if {
	review_cadence_confirmed
	not has_investigation_artefact
	msg := "INCONCLUSIVE: No example investigation artefact found linking a log event to triage and action"
}

generate_message := msg if {
	compliant
	msg := "PASS: Active detections and a weekly review cadence are evidenced, with an example showing a log event led to investigation and action"
}

# ---------------------------
# Helper Functions
# ---------------------------
get_array(obj, key) := value if {
	value := obj[key]
} else := []
