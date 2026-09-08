# METADATA
# title: Deploy a Data Loss Prevention Solution (GCP)
# description: |
#   GCP must use an automated data loss prevention capability to identify
#   sensitive data stored, processed, or transmitted through in-scope cloud
#   assets. Cloud DLP findings must be actionable and integrated with data
#   classification, inventory, monitoring, and remediation workflows.
#
#   The control verifies:
#   - Cloud DLP is deployed and configured
#   - DLP inspection templates and detectors are defined
#   - DLP scanning scope is defined
#   - Exclusions are documented and controlled
#   - In-scope repositories and locations are covered
#   - Recent DLP findings are available
#   - Findings are incorporated into the data inventory
#   - Remediation workflows exist
#   - Remediation is tracked to closure
#
# related_resources:
# - ref: https://cloud.google.com/sensitive-data-protection/docs
#   description: Google Cloud Sensitive Data Protection Documentation
# - ref: https://cloud.google.com/sensitive-data-protection/docs/concepts-dlp-overview
#   description: Cloud DLP Overview
# - ref: https://cloud.google.com/sensitive-data-protection/docs/inspect-data-storage
#   description: Cloud DLP Data Inspection Documentation
# - ref: https://cloud.google.com/asset-inventory/docs
#   description: Google Cloud Asset Inventory Documentation
#
# custom:
#   control_id: CIS-3.13
#   framework: cis
#   benchmark: gcp-foundations
#   version: v2.0.0
#   safeguard: 3.13
#   severity: high
#   service: Cloud DLP
#   asset_type: Data
#   implementation_group: 3
#   requires_permissions:
#   - dlp.inspectTemplates.get
#   - dlp.inspectTemplates.list
#   - dlp.dlpJobs.get
#   - dlp.dlpJobs.list
#   - dlp.storedInfoTypes.get
#   - dlp.storedInfoTypes.list
#   - cloudasset.assets.list
#   - logging.viewer

package cis.gcp_foundations.v2_0_0.control_3_13

import rego.v1

# ---------------------------
# Default Result
# ---------------------------
default result := {
  "compliant": false,
  "message": "Evaluation failed: insufficient Data Loss Prevention evidence",
  "details": {}
}

default compliant := false

# ---------------------------
# Compliance Logic
# ---------------------------
compliant if {
  input.dlp_deployed == true
  input.dlp_policy_configured == true
  input.dlp_scope_defined == true
  input.dlp_coverage_verified == true
  input.recent_findings_available == true
  input.inventory_update_workflow_defined == true
  input.remediation_workflow_defined == true
  input.remediation_tracked_to_closure == true
  valid_dlp_configuration
  valid_dlp_coverage
  valid_findings
  valid_remediation
  valid_inventory_integration
}

# ---------------------------
# Validate DLP Configuration
# ---------------------------
valid_dlp_configuration if {
  some template in input.dlp_templates

  template.template_id != ""
  template.name != ""
  template.detectors != ""
  template.scope != ""
}

# ---------------------------
# Validate DLP Coverage
# ---------------------------
valid_dlp_coverage if {
  some scope in input.dlp_scopes

  scope.project_id != ""
  scope.repository != ""
  scope.location != ""
  scope.scan_enabled == true
}

# ---------------------------
# Validate DLP Findings
# ---------------------------
valid_findings if {
  some finding in input.dlp_findings

  finding.finding_id != ""
  finding.timestamp != ""
  finding.resource != ""
  finding.sensitive_data_type != ""
  finding.severity != ""
  finding.status != ""
}

# ---------------------------
# Validate Remediation Evidence
# ---------------------------
valid_remediation if {
  some remediation in input.remediation_records

  remediation.finding_id != ""
  remediation.action != ""
  remediation.owner != ""
  remediation.ticket_id != ""
  remediation.created_timestamp != ""
  remediation.status != ""
  remediation.closure_timestamp != ""
}

# ---------------------------
# Validate Inventory Integration
# ---------------------------
valid_inventory_integration if {
  some update in input.inventory_updates

  update.finding_id != ""
  update.resource != ""
  update.inventory_record != ""
  update.update_timestamp != ""
  update.update_action != ""
}

# ---------------------------
# Result Output
# ---------------------------
result := output if {
  findings := get_array(input, "dlp_findings")
  templates := get_array(input, "dlp_templates")
  scopes := get_array(input, "dlp_scopes")
  remediation := get_array(input, "remediation_records")
  inventory_updates := get_array(input, "inventory_updates")

  output := {
    "compliant": compliant,
    "message": generate_message,
    "affected_resources": findings,
    "details": {
      "dlp_deployed":
          input.dlp_deployed,
      "dlp_policy_configured":
          input.dlp_policy_configured,
      "dlp_scope_defined":
          input.dlp_scope_defined,
      "dlp_coverage_verified":
          input.dlp_coverage_verified,
      "recent_findings_available":
          input.recent_findings_available,
      "inventory_update_workflow_defined":
          input.inventory_update_workflow_defined,
      "remediation_workflow_defined":
          input.remediation_workflow_defined,
      "remediation_tracked_to_closure":
          input.remediation_tracked_to_closure,
      "dlp_template_count":
          count(templates),
      "dlp_scope_count":
          count(scopes),
      "finding_count":
          count(findings),
      "remediation_record_count":
          count(remediation),
      "inventory_update_count":
          count(inventory_updates),
      "requires_example_evidence": true
    }
  }
}

# ---------------------------
# Message Logic
# ---------------------------
generate_message := msg if {
  not input.dlp_deployed
  msg := "FAIL: No automated Cloud DLP solution is deployed"
}

generate_message := msg if {
  input.dlp_deployed
  not input.dlp_policy_configured
  msg := "FAIL: Cloud DLP is deployed but no inspection policy or configuration is defined"
}

generate_message := msg if {
  input.dlp_policy_configured
  not valid_dlp_configuration
  msg := "INCONCLUSIVE: DLP configuration exists but templates, detectors, or scope evidence is incomplete"
}

generate_message := msg if {
  valid_dlp_configuration
  not input.dlp_scope_defined
  msg := "FAIL: Cloud DLP scanning scope is not defined"
}

generate_message := msg if {
  input.dlp_scope_defined
  not input.dlp_coverage_verified
  msg := "FAIL: DLP coverage for in-scope repositories, projects, or locations cannot be verified"
}

generate_message := msg if {
  input.dlp_coverage_verified
  not valid_dlp_coverage
  msg := "INCONCLUSIVE: DLP coverage is claimed but repository, project, location, or scan configuration evidence is incomplete"
}

generate_message := msg if {
  valid_dlp_coverage
  not input.recent_findings_available
  msg := "FAIL: No recent Cloud DLP findings are available to demonstrate operational use"
}

generate_message := msg if {
  input.recent_findings_available
  not valid_findings
  msg := "INCONCLUSIVE: DLP findings exist but finding identifiers, timestamps, affected resources, or sensitive-data classifications are incomplete"
}

generate_message := msg if {
  valid_findings
  not input.inventory_update_workflow_defined
  msg := "FAIL: DLP findings are not connected to a documented data inventory update workflow"
}

generate_message := msg if {
  input.inventory_update_workflow_defined
  not valid_inventory_integration
  msg := "INCONCLUSIVE: Inventory integration is claimed but evidence showing DLP findings updating inventory records is incomplete"
}

generate_message := msg if {
  valid_inventory_integration
  not input.remediation_workflow_defined
  msg := "FAIL: No documented remediation workflow exists for actionable DLP findings"
}

generate_message := msg if {
  input.remediation_workflow_defined
  not input.remediation_tracked_to_closure
  msg := "FAIL: DLP findings are not tracked through remediation to closure"
}

generate_message := msg if {
  input.remediation_tracked_to_closure
  not valid_remediation
  msg := "INCONCLUSIVE: Remediation is claimed but ownership, ticketing, timestamps, or closure evidence is incomplete"
}

generate_message := msg if {
  valid_remediation
  not compliant
  msg := "INCONCLUSIVE: Cloud DLP is deployed but coverage, findings, inventory integration, or remediation evidence could not be fully verified"
}

generate_message := msg if {
  compliant
  msg := "PASS: Cloud DLP is deployed with defined coverage, produces actionable findings, updates the data inventory, and tracks remediation through closure"
}

# ---------------------------
# Helper Functions
# ---------------------------
get_array(obj, key) := value if {
  value := obj[key]
} else := []
