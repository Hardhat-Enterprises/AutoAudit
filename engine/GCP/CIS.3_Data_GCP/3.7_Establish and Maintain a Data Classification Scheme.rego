# METADATA
# title: Establish and Maintain a Data Classification Scheme (GCP)
# description: |
#   GCP data must be classified according to an enterprise-wide data
#   classification scheme. Classification labels must be defined, applied to
#   in-scope data assets, and measurable through coverage reporting.
#
#   The control verifies:
#   - An approved classification scheme exists
#   - Classification labels are defined
#   - Labels are mapped to GCP tags or policy tags
#   - Classification is applied to real data assets
#   - Classification coverage is measurable
#   - Unclassified assets are identified and handled
#   - Cloud DLP discovery evidence supports classification where applicable
#   - The classification scheme is reviewed annually
#
# related_resources:
# - ref: https://cloud.google.com/dataplex/docs
#   description: Google Cloud Dataplex Documentation
# - ref: https://cloud.google.com/bigquery/docs/column-level-security
#   description: BigQuery Column-Level Security Documentation
# - ref: https://cloud.google.com/sensitive-data-protection/docs
#   description: Google Cloud Sensitive Data Protection Documentation
#
# custom:
#   control_id: CIS-3.7
#   framework: cis
#   benchmark: gcp-foundations
#   version: v2.0.0
#   safeguard: 3.7
#   severity: high
#   service: Data Classification
#   asset_type: Data
#   implementation_group: 2
#   requires_permissions:
#   - dataplex.entries.get
#   - dataplex.entries.list
#   - bigquery.datasets.get
#   - bigquery.tables.get
#   - dlp.inspectTemplates.get
#   - dlp.jobs.get
#   - logging.viewer

package cis.gcp_foundations.v2_0_0.control_3_7

import rego.v1

# ---------------------------
# Default Result
# ---------------------------
default result := {
  "compliant": false,
  "message": "Evaluation failed: insufficient data classification evidence",
  "details": {}
}

default compliant := false

# ---------------------------
# Compliance Logic
# ---------------------------
compliant if {
  input.classification_scheme_exists == true
  input.classification_labels_defined == true
  input.label_mapping_defined == true
  input.classification_applied == true
  input.coverage_reporting_available == true
  input.unclassified_assets_handled == true
  input.annual_review_completed == true
  valid_classification_scheme
  valid_classification_coverage
  valid_review_evidence
}

# ---------------------------
# Validate Classification Scheme
# ---------------------------
valid_classification_scheme if {
  input.classification_scheme_name != ""
  input.classification_scheme_version != ""
  input.classification_scheme_approval_date != ""

  some label in input.classification_labels

  label.name != ""
  label.description != ""
  label.sensitivity_level != ""
}

# ---------------------------
# Validate Classification Mapping
# ---------------------------
valid_label_mapping if {
  some mapping in input.classification_mappings

  mapping.label != ""
  mapping.gcp_metadata_type != ""
  mapping.metadata_name != ""
}

# ---------------------------
# Validate Classification Coverage
# ---------------------------
valid_classification_coverage if {
  input.in_scope_asset_count >= 0
  input.classified_asset_count >= 0
  input.unclassified_asset_count >= 0

  input.classified_asset_count <= input.in_scope_asset_count
  input.unclassified_asset_count <= input.in_scope_asset_count

  input.coverage_report_date != ""
}

# ---------------------------
# Validate DLP Discovery Evidence
# ---------------------------
valid_dlp_evidence if {
  input.dlp_discovery_enabled == true
  input.dlp_last_scan_timestamp != ""
  input.dlp_findings_summary != ""
}

# ---------------------------
# Validate Annual Review Evidence
# ---------------------------
valid_review_evidence if {
  input.annual_review_completed == true
  input.review_date != ""
  input.review_reviewer != ""
  input.review_outcome != ""
}

# ---------------------------
# Result Output
# ---------------------------
result := output if {
  assets := get_array(input, "classified_assets")
  labels := get_array(input, "classification_labels")
  mappings := get_array(input, "classification_mappings")

  output := {
    "compliant": compliant,
    "message": generate_message,
    "affected_resources": assets,
    "details": {
      "classification_scheme_exists":
          input.classification_scheme_exists,
      "classification_scheme_name":
          input.classification_scheme_name,
      "classification_scheme_version":
          input.classification_scheme_version,
      "classification_scheme_approval_date":
          input.classification_scheme_approval_date,
      "classification_labels_defined":
          input.classification_labels_defined,
      "label_mapping_defined":
          input.label_mapping_defined,
      "classification_applied":
          input.classification_applied,
      "coverage_reporting_available":
          input.coverage_reporting_available,
      "unclassified_assets_handled":
          input.unclassified_assets_handled,
      "in_scope_asset_count":
          input.in_scope_asset_count,
      "classified_asset_count":
          input.classified_asset_count,
      "unclassified_asset_count":
          input.unclassified_asset_count,
      "coverage_report_date":
          input.coverage_report_date,
      "dlp_discovery_enabled":
          input.dlp_discovery_enabled,
      "dlp_last_scan_timestamp":
          input.dlp_last_scan_timestamp,
      "dlp_findings_summary":
          input.dlp_findings_summary,
      "annual_review_completed":
          input.annual_review_completed,
      "review_date":
          input.review_date,
      "review_reviewer":
          input.review_reviewer,
      "review_outcome":
          input.review_outcome,
      "classification_label_count":
          count(labels),
      "classification_mapping_count":
          count(mappings),
      "classified_asset_sample_count":
          count(assets),
      "requires_example_evidence": true
    }
  }
}

# ---------------------------
# Message Logic
# ---------------------------
generate_message := msg if {
  not input.classification_scheme_exists
  msg := "FAIL: No enterprise-wide data classification scheme found"
}

generate_message := msg if {
  input.classification_scheme_exists
  not input.classification_labels_defined
  msg := "FAIL: Data classification labels are not defined"
}

generate_message := msg if {
  input.classification_labels_defined
  not valid_classification_scheme
  msg := "INCONCLUSIVE: Classification scheme exists but label definitions or approval evidence could not be fully verified"
}

generate_message := msg if {
  valid_classification_scheme
  not input.label_mapping_defined
  msg := "FAIL: Classification labels are not mapped to GCP tags or policy tags"
}

generate_message := msg if {
  input.label_mapping_defined
  not valid_label_mapping
  msg := "INCONCLUSIVE: Classification mappings exist but metadata implementation cannot be fully verified"
}

generate_message := msg if {
  valid_label_mapping
  not input.classification_applied
  msg := "FAIL: Classification labels are not applied to in-scope GCP data assets"
}

generate_message := msg if {
  input.classification_applied
  not input.coverage_reporting_available
  msg := "FAIL: No classification coverage report is available for the in-scope data estate"
}

generate_message := msg if {
  input.coverage_reporting_available
  not valid_classification_coverage
  msg := "INCONCLUSIVE: Classification coverage is reported but asset counts or coverage evidence cannot be validated"
}

generate_message := msg if {
  valid_classification_coverage
  not input.unclassified_assets_handled
  msg := "FAIL: Unclassified data assets are not identified or handled through a defined process"
}

generate_message := msg if {
  input.unclassified_assets_handled
  input.dlp_discovery_enabled
  not valid_dlp_evidence
  msg := "INCONCLUSIVE: Cloud DLP discovery is enabled but recent findings evidence is incomplete"
}

generate_message := msg if {
  input.unclassified_assets_handled
  not input.annual_review_completed
  msg := "FAIL: No evidence of an annual review of the data classification scheme"
}

generate_message := msg if {
  input.annual_review_completed
  not valid_review_evidence
  msg := "INCONCLUSIVE: Classification scheme review is recorded but reviewer, date, or outcome evidence is incomplete"
}

generate_message := msg if {
  valid_review_evidence
  not compliant
  msg := "INCONCLUSIVE: Classification scheme exists but application, coverage, unclassified asset handling, or review evidence could not be fully verified"
}

generate_message := msg if {
  compliant
  msg := "PASS: GCP data classification is defined, applied to in-scope assets with measurable coverage, supported by discovery where applicable, and reviewed annually"
}

# ---------------------------
# Helper Functions
# ---------------------------
get_array(obj, key) := value if {
  value := obj[key]
} else := []
