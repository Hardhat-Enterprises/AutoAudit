# METADATA
# title: Establish and Maintain a Data Inventory (GCP)
# description: |
#   Data within GCP must be inventoried based on the enterprise data management
#   process. The inventory must cover in-scope data stores and key datasets,
#   prioritize sensitive data, contain required inventory metadata, and be
#   refreshed on a defined cadence with evidence of annual review.
#
#   The control verifies:
#   - Data inventory exists
#   - Inventory scope and coverage are defined
#   - Required inventory metadata is captured
#   - Inventory refresh cadence is defined and evidenced
#   - Cloud DLP sensitive data discovery evidence exists
#   - Sensitive data findings are incorporated or tracked in the inventory
#   - Annual inventory review or attestation is completed
#
# related_resources:
# - ref: https://cloud.google.com/dataplex/docs
#   description: Google Cloud Dataplex Documentation
# - ref: https://cloud.google.com/asset-inventory/docs
#   description: Google Cloud Asset Inventory Documentation
# - ref: https://cloud.google.com/sensitive-data-protection/docs
#   description: Sensitive Data Protection Documentation
# - ref: https://cloud.google.com/scheduler/docs
#   description: Cloud Scheduler Documentation
#
# custom:
#   control_id: CIS-3.2
#   framework: cis
#   benchmark: gcp-foundations
#   version: v2.0.0
#   safeguard: 3.2
#   severity: high
#   service: Data Inventory
#   asset_type: Data
#   implementation_group: 1
#   requires_permissions:
#   - dataplex.catalogs.get
#   - dataplex.entries.get
#   - cloudasset.assets.list
#   - cloudasset.viewer
#   - dlp.jobs.get
#   - dlp.inspectTemplates.get
#   - logging.viewer

package cis.gcp_foundations.v2_0_0.control_3_2

import rego.v1

# ---------------------------
# Default Result
# ---------------------------
default result := {
  "compliant": false,
  "message": "Evaluation failed: insufficient data inventory evidence",
  "details": {}
}

default compliant := false

# ---------------------------
# Compliance Logic
# ---------------------------
compliant if {
  input.inventory_exists == true
  input.inventory_scope_defined == true
  input.required_metadata_present == true
  input.refresh_schedule_defined == true
  input.refresh_execution_verified == true
  input.dlp_discovery_enabled == true
  input.sensitive_data_tracking_verified == true
  input.annual_review_completed == true
  valid_inventory
  valid_review_evidence
}

# ---------------------------
# Validate Inventory
# ---------------------------
required_metadata_present if {
  every item in input.inventory {
    item.resource_name != ""
    item.resource_type != ""
    item.location != ""
    item.owner != ""
    item.classification != ""
    item.business_context != ""
    item.last_review_date != ""
  }
}

valid_inventory if {
  count(input.inventory) > 0
  required_metadata_present
}

# ---------------------------
# Validate Sensitive Data Discovery
# ---------------------------
sensitive_data_discovery_verified if {
  input.dlp_discovery_enabled == true
  input.dlp_findings_summary != ""
  input.dlp_last_scan_timestamp != ""
}

# ---------------------------
# Validate Sensitive Data Tracking
# ---------------------------
sensitive_data_tracking_verified if {
  input.sensitive_data_tracking_verified == true
  sensitive_data_discovery_verified
}

# ---------------------------
# Validate Refresh Evidence
# ---------------------------
refresh_execution_verified if {
  input.refresh_frequency_days > 0
  input.last_refresh_timestamp != ""
  input.refresh_last_run_status == "SUCCESS"
}

# ---------------------------
# Validate Annual Review Evidence
# ---------------------------
valid_review_evidence if {
  input.annual_review_completed == true
  input.review_date != ""
  input.review_reviewer != ""
  input.review_attestation != ""
}

# ---------------------------
# Result Output
# ---------------------------
result := output if {
  inventory := get_array(input, "inventory")

  output := {
    "compliant": compliant,
    "message": generate_message,
    "affected_resources": inventory,
    "details": {
      "inventory_exists": input.inventory_exists,
      "inventory_scope": input.inventory_scope,
      "inventory_scope_defined": input.inventory_scope_defined,
      "required_metadata_present": input.required_metadata_present,
      "refresh_schedule_defined": input.refresh_schedule_defined,
      "refresh_frequency_days": input.refresh_frequency_days,
      "last_refresh_timestamp": input.last_refresh_timestamp,
      "refresh_last_run_status": input.refresh_last_run_status,
      "dlp_discovery_enabled": input.dlp_discovery_enabled,
      "dlp_last_scan_timestamp": input.dlp_last_scan_timestamp,
      "dlp_findings_summary": input.dlp_findings_summary,
      "sensitive_data_tracking_verified":
          input.sensitive_data_tracking_verified,
      "annual_review_completed": input.annual_review_completed,
      "review_date": input.review_date,
      "review_reviewer": input.review_reviewer,
      "review_attestation": input.review_attestation,
      "inventory_count": count(inventory),
      "requires_example_evidence": true
    }
  }
}

# ---------------------------
# Message Logic
# ---------------------------
generate_message := msg if {
  not input.inventory_exists
  msg := "FAIL: No enterprise data inventory found"
}

generate_message := msg if {
  input.inventory_exists
  not input.inventory_scope_defined
  msg := "FAIL: Data inventory scope is not defined"
}

generate_message := msg if {
  input.inventory_scope_defined
  not valid_inventory
  msg := "FAIL: Data inventory is missing required fields or contains no inventoried data stores or datasets"
}

generate_message := msg if {
  valid_inventory
  not input.refresh_schedule_defined
  msg := "FAIL: No defined data inventory refresh cadence found"
}

generate_message := msg if {
  input.refresh_schedule_defined
  not input.refresh_execution_verified
  msg := "INCONCLUSIVE: Data inventory refresh cadence is defined but execution evidence is missing or unsuccessful"
}

generate_message := msg if {
  input.refresh_execution_verified
  not input.dlp_discovery_enabled
  msg := "FAIL: Cloud DLP sensitive data discovery is not enabled for in-scope data"
}

generate_message := msg if {
  input.dlp_discovery_enabled
  not sensitive_data_discovery_verified
  msg := "INCONCLUSIVE: Cloud DLP discovery is enabled but recent scan or findings evidence is missing"
}

generate_message := msg if {
  sensitive_data_discovery_verified
  not input.sensitive_data_tracking_verified
  msg := "FAIL: Sensitive data discovery findings are not incorporated into or explicitly tracked by the data inventory"
}

generate_message := msg if {
  input.sensitive_data_tracking_verified
  not input.annual_review_completed
  msg := "FAIL: No evidence of an annual data inventory review or attestation"
}

generate_message := msg if {
  input.annual_review_completed
  not valid_review_evidence
  msg := "INCONCLUSIVE: Annual inventory review is recorded but reviewer, date, or attestation evidence is incomplete"
}

generate_message := msg if {
  valid_review_evidence
  not compliant
  msg := "INCONCLUSIVE: Data inventory exists but freshness, sensitive data coverage, or review evidence could not be fully verified"
}

generate_message := msg if {
  compliant
  msg := "PASS: GCP data inventory is established, maintained, refreshed on schedule, incorporates sensitive data discovery, and is reviewed annually"
}

# ---------------------------
# Helper Functions
# ---------------------------
get_array(obj, key) := value if {
  value := obj[key]
} else := []
