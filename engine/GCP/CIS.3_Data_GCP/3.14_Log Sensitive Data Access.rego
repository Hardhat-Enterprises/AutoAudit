# METADATA
# title: Log Sensitive Data Access (GCP)
# description: |
#   Access to sensitive data must be logged so that reads, writes,
#   modifications, and disposal activities can be traced to the responsible
#   principal. Logs must be centralised, retained according to enterprise or
#   regulatory requirements, and used to support detection and investigation
#   of high-risk access patterns.
#
#   The control verifies:
#   - Data Access audit logging is enabled for sensitive data stores
#   - Access by principals can be reconstructed
#   - Logs are centralised through an organisation-level Logs Router sink
#   - Log retention requirements are defined and met
#   - A protected central logging destination or SIEM is used
#   - Representative sensitive data access events are available
#   - High-risk access detection is configured
#   - At least one alert or investigation example exists
#
# related_resources:
# - ref: https://cloud.google.com/logging/docs/audit
#   description: Cloud Audit Logs Documentation
# - ref: https://cloud.google.com/logging/docs/audit/configure-data-access
#   description: Configure Data Access Audit Logs Documentation
# - ref: https://cloud.google.com/logging/docs/routing/overview
#   description: Cloud Logging Logs Router Documentation
# - ref: https://cloud.google.com/logging/docs/log-analytics
#   description: Cloud Logging and Log Analytics Documentation
#
# custom:
#   control_id: CIS-3.14
#   framework: cis
#   benchmark: gcp-foundations
#   version: v2.0.0
#   safeguard: 3.14
#   severity: high
#   service: Cloud Logging / Cloud Audit Logs
#   asset_type: Data
#   implementation_group: 3
#   requires_permissions:
#   - logging.viewer
#   - logging.privateLogEntries.list
#   - logging.sinks.get
#   - logging.sinks.list
#   - logging.settings.get
#   - resourcemanager.projects.get
#
package cis.gcp_foundations.v2_0_0.control_3_14

import rego.v1

# ---------------------------
# Default Result
# ---------------------------
default result := {
  "compliant": false,
  "message": "Evaluation failed: insufficient sensitive data access logging evidence",
  "details": {}
}

default compliant := false

# ---------------------------
# Compliance Logic
# ---------------------------
compliant if {
  input.data_access_logging_enabled == true
  input.sensitive_store_coverage_verified == true
  input.principal_access_traceable == true
  input.logs_centralised == true
  input.retention_policy_defined == true
  input.retention_requirement_met == true
  input.protected_log_destination == true
  input.representative_access_event_available == true
  input.high_risk_detection_enabled == true
  input.alert_or_investigation_example_available == true
  valid_sensitive_store_coverage
  valid_sink_configuration
  valid_retention_configuration
  valid_access_event
  valid_detection_evidence
}

# ---------------------------
# Validate Sensitive Store Coverage
# ---------------------------
valid_sensitive_store_coverage if {
  some store in input.sensitive_data_stores

  store.resource_name != ""
  store.resource_type != ""
  store.project_id != ""
  store.data_access_logging_enabled == true
  store.logging_scope != ""
}

# ---------------------------
# Validate Logs Router Configuration
# ---------------------------
valid_sink_configuration if {
  input.logs_centralised == true
  input.organization_sink_name != ""
  input.sink_destination != ""
  input.sink_destination_type != ""
  input.sink_filter != ""
  input.sink_status == "ACTIVE"
}

# ---------------------------
# Validate Retention Configuration
# ---------------------------
valid_retention_configuration if {
  input.retention_policy_defined == true
  input.retention_days > 0
  input.required_retention_days > 0
  input.retention_days >= input.required_retention_days
  input.retention_review_date != ""
}

# ---------------------------
# Validate Representative Access Event
# ---------------------------
valid_access_event if {
  input.representative_access_event_available == true
  input.access_event_principal != ""
  input.access_event_resource != ""
  input.access_event_action != ""
  input.access_event_timestamp != ""
  input.access_event_source != ""
}

# ---------------------------
# Validate Detection Evidence
# ---------------------------
valid_detection_evidence if {
  input.high_risk_detection_enabled == true
  input.detection_rule_name != ""
  input.detection_pattern != ""
  input.alert_or_investigation_example_available == true
  input.alert_or_investigation_timestamp != ""
  input.alert_or_investigation_status != ""
}

# ---------------------------
# Result Output
# ---------------------------
result := output if {
  stores := get_array(input, "sensitive_data_stores")
  alerts := get_array(input, "detection_examples")
  sinks := get_array(input, "logging_sinks")

  output := {
    "compliant": compliant,
    "message": generate_message,
    "affected_resources": stores,
    "details": {
      "data_access_logging_enabled":
          input.data_access_logging_enabled,
      "sensitive_store_coverage_verified":
          input.sensitive_store_coverage_verified,
      "principal_access_traceable":
          input.principal_access_traceable,
      "logs_centralised":
          input.logs_centralised,
      "retention_policy_defined":
          input.retention_policy_defined,
      "retention_days":
          input.retention_days,
      "required_retention_days":
          input.required_retention_days,
      "retention_requirement_met":
          input.retention_requirement_met,
      "protected_log_destination":
          input.protected_log_destination,
      "representative_access_event_available":
          input.representative_access_event_available,
      "access_event_principal":
          input.access_event_principal,
      "access_event_resource":
          input.access_event_resource,
      "access_event_action":
          input.access_event_action,
      "access_event_timestamp":
          input.access_event_timestamp,
      "access_event_source":
          input.access_event_source,
      "high_risk_detection_enabled":
          input.high_risk_detection_enabled,
      "detection_rule_name":
          input.detection_rule_name,
      "detection_pattern":
          input.detection_pattern,
      "alert_or_investigation_example_available":
          input.alert_or_investigation_example_available,
      "alert_or_investigation_timestamp":
          input.alert_or_investigation_timestamp,
      "alert_or_investigation_status":
          input.alert_or_investigation_status,
      "sensitive_store_count":
          count(stores),
      "logging_sink_count":
          count(sinks),
      "detection_example_count":
          count(alerts),
      "requires_example_evidence": true
    }
  }
}

# ---------------------------
# Message Logic
# ---------------------------
generate_message := msg if {
  not input.data_access_logging_enabled
  msg := "FAIL: Data Access audit logging is not enabled for sensitive data stores"
}

generate_message := msg if {
  input.data_access_logging_enabled
  not input.sensitive_store_coverage_verified
  msg := "FAIL: Data Access logging coverage for sensitive data stores cannot be verified"
}

generate_message := msg if {
  input.sensitive_store_coverage_verified
  not valid_sensitive_store_coverage
  msg := "INCONCLUSIVE: Sensitive store logging is claimed but resource coverage or logging scope evidence is incomplete"
}

generate_message := msg if {
  valid_sensitive_store_coverage
  not input.principal_access_traceable
  msg := "FAIL: Sensitive data access cannot be reliably traced to individual principals"
}

generate_message := msg if {
  input.principal_access_traceable
  not input.logs_centralised
  msg := "FAIL: Sensitive data access logs are not centralised through an appropriate logging destination"
}

generate_message := msg if {
  input.logs_centralised
  not valid_sink_configuration
  msg := "INCONCLUSIVE: Log centralisation is claimed but organisation-level sink configuration or destination evidence is incomplete"
}

generate_message := msg if {
  valid_sink_configuration
  not input.retention_policy_defined
  msg := "FAIL: No defined retention policy exists for sensitive data access logs"
}

generate_message := msg if {
  input.retention_policy_defined
  not valid_retention_configuration
  msg := "FAIL: Sensitive data access log retention does not meet the required enterprise or regulatory retention period"
}

generate_message := msg if {
  valid_retention_configuration
  not input.retention_requirement_met
  msg := "FAIL: Sensitive data access logs are not retained for the required period"
}

generate_message := msg if {
  input.retention_requirement_met
  not input.protected_log_destination
  msg := "FAIL: Sensitive data access logs are not stored in a protected central logging destination or SIEM"
}

generate_message := msg if {
  input.protected_log_destination
  not input.representative_access_event_available
  msg := "INCONCLUSIVE: Data Access logging is configured but no representative sensitive data access event is available"
}

generate_message := msg if {
  input.representative_access_event_available
  not valid_access_event
  msg := "INCONCLUSIVE: Representative access log exists but principal, resource, action, timestamp, or source evidence is incomplete"
}

generate_message := msg if {
  valid_access_event
  not input.high_risk_detection_enabled
  msg := "FAIL: No detection capability is configured for high-risk sensitive data access patterns"
}

generate_message := msg if {
  input.high_risk_detection_enabled
  not valid_detection_evidence
  msg := "INCONCLUSIVE: High-risk access detection is configured but alert or investigation evidence is incomplete"
}

generate_message := msg if {
  valid_detection_evidence
  not input.alert_or_investigation_example_available
  msg := "FAIL: No alert or investigation example demonstrates operational use of sensitive data access logs"
}

generate_message := msg if {
  input.alert_or_investigation_example_available
  not compliant
  msg := "INCONCLUSIVE: Sensitive data access logging exists but coverage, centralisation, retention, or detection evidence could not be fully verified"
}

generate_message := msg if {
  compliant
  msg := "PASS: Sensitive data access is logged, centralised, retained appropriately, traceable to principals, and used for detection and investigation"
}

# ---------------------------
# Helper Functions
# ---------------------------
get_array(obj, key) := value if {
  value := obj[key]
} else := []
