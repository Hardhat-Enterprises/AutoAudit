# METADATA
# title: Securely Dispose of Data (GCP)
# description: |
#   Data within GCP must be securely disposed of according to the enterprise's
#   documented data management process. Disposal methods must be appropriate
#   to the sensitivity of the data and must address primary data, backups,
#   replicas, and applicable exceptions such as legal holds.
#
#   The control verifies:
#   - Approved data disposal procedure exists
#   - Disposal requirements are aligned to data sensitivity
#   - Cloud Storage lifecycle or deletion controls are configured
#   - Backup and replica disposal is addressed
#   - Disposal execution evidence exists
#   - Legal holds are managed as controlled exceptions
#   - A completed disposal example can be demonstrated
#   - Audit evidence supports completed disposal
#
# related_resources:
# - ref: https://cloud.google.com/storage/docs/lifecycle
#   description: Cloud Storage Object Lifecycle Management Documentation
# - ref: https://cloud.google.com/storage/docs/deleting-buckets
#   description: Cloud Storage Deletion Documentation
# - ref: https://cloud.google.com/kms/docs
#   description: Cloud Key Management Service Documentation
# - ref: https://cloud.google.com/logging/docs/audit
#   description: Cloud Audit Logs Overview
#
# custom:
#   control_id: CIS-3.5
#   framework: cis
#   benchmark: gcp-foundations
#   version: v2.0.0
#   safeguard: 3.5
#   severity: high
#   service: Data Disposal
#   asset_type: Data
#   implementation_group: 1
#   requires_permissions:
#   - storage.buckets.get
#   - storage.objects.get
#   - storage.objects.list
#   - cloudkms.cryptoKeys.get
#   - cloudkms.cryptoKeys.list
#   - logging.viewer

package cis.gcp_foundations.v2_0_0.control_3_5

import rego.v1

# ---------------------------
# Default Result
# ---------------------------
default result := {
  "compliant": false,
  "message": "Evaluation failed: insufficient data disposal evidence",
  "details": {}
}

default compliant := false

# ---------------------------
# Compliance Logic
# ---------------------------
compliant if {
  input.disposal_procedure_exists == true
  input.sensitivity_based_disposal_defined == true
  input.primary_data_disposal_configured == true
  input.backup_disposal_addressed == true
  input.replica_disposal_addressed == true
  input.legal_holds_managed == true
  input.disposal_execution_evidence_available == true
  input.completed_disposal_sample_available == true
  valid_disposal_procedure
  valid_disposal_controls
  valid_disposal_sample
  valid_legal_hold_evidence
}

# ---------------------------
# Validate Disposal Procedure
# ---------------------------
valid_disposal_procedure if {
  input.disposal_procedure_name != ""
  input.disposal_procedure_version != ""
  input.disposal_procedure_approval_date != ""

  some policy in input.disposal_requirements

  policy.data_class != ""
  policy.disposal_method != ""
  policy.sensitivity_level != ""
}

# ---------------------------
# Validate Disposal Controls
# ---------------------------
valid_disposal_controls if {
  some control in input.disposal_controls

  control.resource_name != ""
  control.resource_type != ""
  control.disposal_method != ""
  control.lifecycle_or_deletion_rule != ""
  control.execution_status == "SUCCESS"
}

# ---------------------------
# Validate Disposal Sample
# ---------------------------
valid_disposal_sample if {
  input.disposal_sample.disposal_id != ""
  input.disposal_sample.resource_name != ""
  input.disposal_sample.disposal_date != ""
  input.disposal_sample.disposal_method != ""
  input.disposal_sample.audit_log_reference != ""
}

# ---------------------------
# Validate Legal Hold Evidence
# ---------------------------
valid_legal_hold_evidence if {
  every hold in get_array(input, "legal_holds") {
    hold.hold_id != ""
    hold.resource_name != ""
    hold.reason != ""
    hold.approver != ""
    hold.status != ""
  }
}

# ---------------------------
# Result Output
# ---------------------------
result := output if {
  requirements := get_array(input, "disposal_requirements")
  controls := get_array(input, "disposal_controls")
  legal_holds := get_array(input, "legal_holds")

  output := {
    "compliant": compliant,
    "message": generate_message,
    "affected_resources": controls,
    "details": {
      "disposal_procedure_exists":
          input.disposal_procedure_exists,
      "disposal_procedure_name":
          input.disposal_procedure_name,
      "disposal_procedure_version":
          input.disposal_procedure_version,
      "disposal_procedure_approval_date":
          input.disposal_procedure_approval_date,
      "sensitivity_based_disposal_defined":
          input.sensitivity_based_disposal_defined,
      "primary_data_disposal_configured":
          input.primary_data_disposal_configured,
      "backup_disposal_addressed":
          input.backup_disposal_addressed,
      "replica_disposal_addressed":
          input.replica_disposal_addressed,
      "legal_holds_managed":
          input.legal_holds_managed,
      "disposal_execution_evidence_available":
          input.disposal_execution_evidence_available,
      "completed_disposal_sample_available":
          input.completed_disposal_sample_available,
      "disposal_requirement_count":
          count(requirements),
      "disposal_control_count":
          count(controls),
      "legal_hold_count":
          count(legal_holds),
      "disposal_sample":
          input.disposal_sample,
      "requires_example_evidence": true
    }
  }
}

# ---------------------------
# Message Logic
# ---------------------------
generate_message := msg if {
  not input.disposal_procedure_exists
  msg := "FAIL: No approved data disposal procedure found"
}

generate_message := msg if {
  input.disposal_procedure_exists
  not input.sensitivity_based_disposal_defined
  msg := "FAIL: Disposal methods are not defined according to data sensitivity"
}

generate_message := msg if {
  input.sensitivity_based_disposal_defined
  not valid_disposal_procedure
  msg := "INCONCLUSIVE: Disposal procedure exists but disposal methods or sensitivity requirements could not be fully verified"
}

generate_message := msg if {
  valid_disposal_procedure
  not input.primary_data_disposal_configured
  msg := "FAIL: No configured disposal or deletion control exists for primary in-scope data"
}

generate_message := msg if {
  input.primary_data_disposal_configured
  not input.backup_disposal_addressed
  msg := "FAIL: Backup disposal or purge requirements are not addressed"
}

generate_message := msg if {
  input.backup_disposal_addressed
  not input.replica_disposal_addressed
  msg := "FAIL: Replica or disaster recovery disposal requirements are not addressed"
}

generate_message := msg if {
  input.replica_disposal_addressed
  not input.disposal_execution_evidence_available
  msg := "FAIL: No evidence that data disposal was executed successfully"
}

generate_message := msg if {
  input.disposal_execution_evidence_available
  not valid_disposal_controls
  msg := "INCONCLUSIVE: Disposal controls are claimed but lifecycle or deletion execution evidence is incomplete"
}

generate_message := msg if {
  valid_disposal_controls
  not input.legal_holds_managed
  msg := "FAIL: Legal holds are not managed as controlled disposal exceptions"
}

generate_message := msg if {
  input.legal_holds_managed
  not valid_legal_hold_evidence
  msg := "INCONCLUSIVE: Legal hold management is claimed but hold ownership, approval, or status evidence is incomplete"
}

generate_message := msg if {
  valid_legal_hold_evidence
  not input.completed_disposal_sample_available
  msg := "FAIL: No completed disposal sample is available to demonstrate that disposal actually occurred"
}

generate_message := msg if {
  input.completed_disposal_sample_available
  not valid_disposal_sample
  msg := "INCONCLUSIVE: Disposal sample exists but completion date, method, resource, or audit trail evidence is incomplete"
}

generate_message := msg if {
  valid_disposal_sample
  not compliant
  msg := "INCONCLUSIVE: Data disposal controls exist but backup, replica, legal hold, or execution evidence could not be fully verified"
}

generate_message := msg if {
  compliant
  msg := "PASS: GCP data disposal is defined by sensitivity, implemented for primary data and applicable backups or replicas, supported by execution evidence, and managed with controlled exceptions"
}

# ---------------------------
# Helper Functions
# ---------------------------
get_array(obj, key) := value if {
  value := obj[key]
} else := []
