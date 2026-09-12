# METADATA
# title: Document Data Flows (GCP)
# description: |
#   Data flows must be documented based on the enterprise's data management
#   process and maintained as current architecture documentation. Data flow
#   documentation must identify systems, data stores, trust boundaries, and
#   service providers, and should be linked to concrete GCP resources where
#   applicable.
#
#   The control verifies:
#   - Current data flow documentation exists
#   - Data flow diagrams identify systems and data stores
#   - Trust boundaries and service providers are documented
#   - Diagram elements are linked to real cloud resources
#   - Data flow validation evidence exists through lineage or logs
#   - Documentation is maintained in a controlled repository
#   - Annual review or significant-change review is completed
#   - Ownership and version information are recorded
#
# related_resources:
# - ref: https://cloud.google.com/asset-inventory/docs
#   description: Google Cloud Asset Inventory Documentation
# - ref: https://cloud.google.com/dataplex/docs
#   description: Google Cloud Dataplex Documentation
# - ref: https://cloud.google.com/logging/docs/audit
#   description: Cloud Audit Logs Overview
# - ref: https://cloud.google.com/vpc/docs/flow-logs
#   description: VPC Flow Logs Documentation
#
# custom:
#   control_id: CIS-3.8
#   framework: cis
#   benchmark: gcp-foundations
#   version: v2.0.0
#   safeguard: 3.8
#   severity: high
#   service: Data Flows
#   asset_type: Data
#   implementation_group: 2
#   requires_permissions:
#   - cloudasset.assets.list
#   - cloudasset.viewer
#   - dataplex.entries.get
#   - dataplex.entries.list
#   - logging.viewer

package cis.gcp_foundations.v2_0_0.control_3_8

import rego.v1

# ---------------------------
# Default Result
# ---------------------------
default result := {
  "compliant": false,
  "message": "Evaluation failed: insufficient data flow documentation evidence",
  "details": {}
}

default compliant := false

# ---------------------------
# Compliance Logic
# ---------------------------
compliant if {
  input.data_flow_documented == true
  input.diagram_current == true
  input.systems_and_data_stores_identified == true
  input.trust_boundaries_documented == true
  input.service_providers_documented == true
  input.resource_linkage_verified == true
  input.validation_evidence_available == true
  input.change_controlled_repository == true
  input.review_completed == true
  valid_diagram_metadata
  valid_resource_linkage
  valid_validation_evidence
  valid_review_evidence
}

# ---------------------------
# Validate Diagram Metadata
# ---------------------------
valid_diagram_metadata if {
  input.diagram_name != ""
  input.diagram_version != ""
  input.diagram_date != ""
  input.diagram_owner != ""
}

# ---------------------------
# Validate Resource Linkage
# ---------------------------
valid_resource_linkage if {
  some resource in input.referenced_resources

  resource.resource_name != ""
  resource.resource_type != ""
  resource.resource_identifier != ""
  resource.diagram_reference != ""
}

# ---------------------------
# Validate Flow Validation Evidence
# ---------------------------
valid_validation_evidence if {
  input.validation_evidence_available == true
  input.validation_method != ""
  input.validation_date != ""
  input.validation_resource != ""
  input.validation_result != ""
}

# ---------------------------
# Validate Review Evidence
# ---------------------------
valid_review_evidence if {
  input.review_completed == true
  input.review_date != ""
  input.review_reviewer != ""
  input.review_outcome != ""
}

# ---------------------------
# Result Output
# ---------------------------
result := output if {
  resources := get_array(input, "referenced_resources")
  flows := get_array(input, "documented_flows")
  service_providers := get_array(input, "service_providers")

  output := {
    "compliant": compliant,
    "message": generate_message,
    "affected_resources": resources,
    "details": {
      "data_flow_documented":
          input.data_flow_documented,
      "diagram_name":
          input.diagram_name,
      "diagram_version":
          input.diagram_version,
      "diagram_date":
          input.diagram_date,
      "diagram_owner":
          input.diagram_owner,
      "diagram_current":
          input.diagram_current,
      "systems_and_data_stores_identified":
          input.systems_and_data_stores_identified,
      "trust_boundaries_documented":
          input.trust_boundaries_documented,
      "service_providers_documented":
          input.service_providers_documented,
      "resource_linkage_verified":
          input.resource_linkage_verified,
      "validation_evidence_available":
          input.validation_evidence_available,
      "validation_method":
          input.validation_method,
      "validation_date":
          input.validation_date,
      "validation_resource":
          input.validation_resource,
      "validation_result":
          input.validation_result,
      "change_controlled_repository":
          input.change_controlled_repository,
      "review_completed":
          input.review_completed,
      "review_date":
          input.review_date,
      "review_reviewer":
          input.review_reviewer,
      "review_outcome":
          input.review_outcome,
      "referenced_resource_count":
          count(resources),
      "documented_flow_count":
          count(flows),
      "service_provider_count":
          count(service_providers),
      "requires_example_evidence": true
    }
  }
}

# ---------------------------
# Message Logic
# ---------------------------
generate_message := msg if {
  not input.data_flow_documented
  msg := "FAIL: No documented data flow diagram or equivalent flow documentation found"
}

generate_message := msg if {
  input.data_flow_documented
  not valid_diagram_metadata
  msg := "INCONCLUSIVE: Data flow documentation exists but diagram version, date, or ownership evidence is incomplete"
}

generate_message := msg if {
  valid_diagram_metadata
  not input.diagram_current
  msg := "FAIL: Data flow documentation is outdated and has not been maintained"
}

generate_message := msg if {
  input.diagram_current
  not input.systems_and_data_stores_identified
  msg := "FAIL: Data flow documentation does not identify the relevant systems and data stores"
}

generate_message := msg if {
  input.systems_and_data_stores_identified
  not input.trust_boundaries_documented
  msg := "FAIL: Data flow documentation does not identify applicable trust boundaries"
}

generate_message := msg if {
  input.trust_boundaries_documented
  not input.service_providers_documented
  msg := "FAIL: Applicable service provider or external data flows are not documented"
}

generate_message := msg if {
  input.service_providers_documented
  not input.resource_linkage_verified
  msg := "FAIL: Data flow diagram elements are not linked to concrete cloud resources"
}

generate_message := msg if {
  input.resource_linkage_verified
  not valid_resource_linkage
  msg := "INCONCLUSIVE: Resource linkage is claimed but referenced resource identifiers or diagram mappings are incomplete"
}

generate_message := msg if {
  valid_resource_linkage
  not input.validation_evidence_available
  msg := "FAIL: No evidence validates documented data flows against lineage, audit logs, or network flow logs"
}

generate_message := msg if {
  input.validation_evidence_available
  not valid_validation_evidence
  msg := "INCONCLUSIVE: Data flow validation is claimed but validation method, date, resource, or result evidence is incomplete"
}

generate_message := msg if {
  valid_validation_evidence
  not input.change_controlled_repository
  msg := "FAIL: Data flow documentation is not maintained in a change-controlled repository"
}

generate_message := msg if {
  input.change_controlled_repository
  not input.review_completed
  msg := "FAIL: No evidence of annual or significant-change review of data flow documentation"
}

generate_message := msg if {
  input.review_completed
  not valid_review_evidence
  msg := "INCONCLUSIVE: Data flow review is recorded but reviewer, date, or outcome evidence is incomplete"
}

generate_message := msg if {
  valid_review_evidence
  not compliant
  msg := "INCONCLUSIVE: Data flow documentation exists but resource linkage, validation, ownership, or review evidence could not be fully verified"
}

generate_message := msg if {
  compliant
  msg := "PASS: GCP data flows are documented, linked to real resources, validated through available evidence, maintained under change control, and reviewed periodically"
}

# ---------------------------
# Helper Functions
# ---------------------------
get_array(obj, key) := value if {
  value := obj[key]
} else := []
