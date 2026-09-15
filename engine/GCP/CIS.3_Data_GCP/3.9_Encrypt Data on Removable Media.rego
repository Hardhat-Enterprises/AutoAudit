# METADATA
# title: Encrypt Data on Removable Media (GCP)
# description: |
#   Sensitive data stored or transferred to removable media must be protected
#   through endpoint-layer encryption and appropriate removable media controls.
#   GCP cloud encryption controls such as customer-managed keys must not be
#   treated as a substitute for endpoint removable media encryption.
#
#   The control verifies:
#   - Removable media encryption or control policy exists
#   - Policy scope covers managed endpoints handling sensitive data
#   - Removable media enforcement is enabled
#   - Compliance or enforcement evidence exists
#   - Exceptions are documented and managed
#   - Cloud Audit Logs provide supporting visibility into bulk export activity
#   - Export events can be investigated or alerted on where applicable
#
# related_resources:
# - ref: https://support.google.com/a/topic/24642
#   description: Google Workspace Endpoint Management Documentation
# - ref: https://cloud.google.com/logging/docs/audit
#   description: Cloud Audit Logs Overview
# - ref: https://cloud.google.com/logging/docs/log-analytics
#   description: Cloud Logging and Log Analytics Documentation
#
# custom:
#   control_id: CIS-3.9
#   framework: cis
#   benchmark: gcp-foundations
#   version: v2.0.0
#   safeguard: 3.9
#   severity: high
#   service: Endpoint Management
#   asset_type: Data
#   implementation_group: 2
#   requires_permissions:
#   - logging.viewer
#   - logging.logEntries.list
#
package cis.gcp_foundations.v2_0_0.control_3_9

import rego.v1

# ---------------------------
# Default Result
# ---------------------------
default result := {
  "compliant": false,
  "message": "Evaluation failed: insufficient removable media encryption evidence",
  "details": {}
}

default compliant := false

# ---------------------------
# Compliance Logic
# ---------------------------
compliant if {
  input.removable_media_policy_exists == true
  input.removable_media_scope_defined == true
  input.removable_media_encryption_required == true
  input.removable_media_enforcement_enabled == true
  input.enforcement_evidence_available == true
  input.exceptions_managed == true
  valid_enforcement_evidence
  valid_exception_evidence
}

# ---------------------------
# Validate Enforcement Evidence
# ---------------------------
valid_enforcement_evidence if {
  input.enforcement_evidence_available == true
  input.compliance_report_date != ""
  input.enrolled_device_count >= 0
  input.compliant_device_count >= 0
  input.non_compliant_device_count >= 0

  input.compliant_device_count <= input.enrolled_device_count
  input.non_compliant_device_count <= input.enrolled_device_count
}

# ---------------------------
# Validate Exception Evidence
# ---------------------------
valid_exception_evidence if {
  every exception in get_array(input, "removable_media_exceptions") {
    exception.exception_id != ""
    exception.device_or_user != ""
    exception.reason != ""
    exception.approver != ""
    exception.approval_date != ""
    exception.status != ""
  }
}

# ---------------------------
# Validate Cloud Export Monitoring
# ---------------------------
valid_export_monitoring if {
  input.cloud_export_monitoring_enabled == true
  input.export_event_available == true
  input.export_event_timestamp != ""
  input.export_event_resource != ""
  input.export_event_investigation_status != ""
}

# ---------------------------
# Result Output
# ---------------------------
result := output if {
  exceptions := get_array(input, "removable_media_exceptions")
  export_events := get_array(input, "export_events")

  output := {
    "compliant": compliant,
    "message": generate_message,
    "affected_resources": export_events,
    "details": {
      "removable_media_policy_exists":
          input.removable_media_policy_exists,
      "removable_media_scope_defined":
          input.removable_media_scope_defined,
      "removable_media_encryption_required":
          input.removable_media_encryption_required,
      "removable_media_enforcement_enabled":
          input.removable_media_enforcement_enabled,
      "enforcement_evidence_available":
          input.enforcement_evidence_available,
      "compliance_report_date":
          input.compliance_report_date,
      "enrolled_device_count":
          input.enrolled_device_count,
      "compliant_device_count":
          input.compliant_device_count,
      "non_compliant_device_count":
          input.non_compliant_device_count,
      "exceptions_managed":
          input.exceptions_managed,
      "cloud_export_monitoring_enabled":
          input.cloud_export_monitoring_enabled,
      "export_event_available":
          input.export_event_available,
      "export_event_timestamp":
          input.export_event_timestamp,
      "export_event_resource":
          input.export_event_resource,
      "export_event_investigation_status":
          input.export_event_investigation_status,
      "exception_count":
          count(exceptions),
      "export_event_count":
          count(export_events),
      "requires_example_evidence": true
    }
  }
}

# ---------------------------
# Message Logic
# ---------------------------
generate_message := msg if {
  not input.removable_media_policy_exists
  msg := "FAIL: No removable media encryption or control policy found"
}

generate_message := msg if {
  input.removable_media_policy_exists
  not input.removable_media_scope_defined
  msg := "FAIL: Removable media control scope is not defined for managed endpoints"
}

generate_message := msg if {
  input.removable_media_scope_defined
  not input.removable_media_encryption_required
  msg := "FAIL: Encryption is not required for removable media containing sensitive data"
}

generate_message := msg if {
  input.removable_media_encryption_required
  not input.removable_media_enforcement_enabled
  msg := "FAIL: Removable media encryption or usage controls are not enforced"
}

generate_message := msg if {
  input.removable_media_enforcement_enabled
  not input.enforcement_evidence_available
  msg := "INCONCLUSIVE: Removable media controls are enabled but enforcement or compliance evidence is missing"
}

generate_message := msg if {
  input.enforcement_evidence_available
  not valid_enforcement_evidence
  msg := "INCONCLUSIVE: Compliance reporting exists but device coverage or compliance counts cannot be validated"
}

generate_message := msg if {
  valid_enforcement_evidence
  not input.exceptions_managed
  msg := "FAIL: Removable media control exceptions are not documented or managed"
}

generate_message := msg if {
  input.exceptions_managed
  not valid_exception_evidence
  msg := "INCONCLUSIVE: Removable media exceptions exist but approval, ownership, or status evidence is incomplete"
}

generate_message := msg if {
  valid_exception_evidence
  not input.cloud_export_monitoring_enabled
  msg := "INCONCLUSIVE: Endpoint removable media controls are evidenced, but supporting cloud export monitoring is not enabled"
}

generate_message := msg if {
  input.cloud_export_monitoring_enabled
  not input.export_event_available
  msg := "INCONCLUSIVE: Cloud export monitoring is enabled but no representative sensitive-data export event evidence is available"
}

generate_message := msg if {
  input.export_event_available
  not valid_export_monitoring
  msg := "INCONCLUSIVE: Export activity is available but timestamp, resource, or investigation evidence is incomplete"
}

generate_message := msg if {
  valid_export_monitoring
  not compliant
  msg := "INCONCLUSIVE: Removable media controls exist but enforcement, exception, or supporting export-monitoring evidence could not be fully verified"
}

generate_message := msg if {
  compliant
  msg := "PASS: Removable media encryption and usage controls are enforced for sensitive data, compliance is evidenced, exceptions are managed, and cloud export activity provides supporting visibility"
}

# ---------------------------
# Helper Functions
# ---------------------------
get_array(obj, key) := value if {
  value := obj[key]
} else := []
