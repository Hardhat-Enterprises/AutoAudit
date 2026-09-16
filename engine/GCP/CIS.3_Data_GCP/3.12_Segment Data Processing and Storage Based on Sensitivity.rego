# METADATA
# title: Segment Data Processing and Storage Based on Sensitivity (GCP)
# description: |
#   Sensitive data processing and storage must be isolated from lower-sensitivity
#   environments. GCP resources must be segmented according to data sensitivity
#   using resource hierarchy separation, network boundaries, access controls,
#   and controlled cross-tier pathways.
#
#   The control verifies:
#   - Data sensitivity tiers are defined
#   - GCP folders or projects are separated by sensitivity tier
#   - Sensitive resources are assigned to the appropriate tier
#   - Network and service boundaries are enforced for restricted tiers
#   - IAM groups and roles are separated by tier
#   - Privileged access is controlled per tier
#   - Cross-tier access uses explicit and reviewable mechanisms
#   - Cross-tier access is auditable
#
# related_resources:
# - ref: https://cloud.google.com/resource-manager/docs/cloud-platform-resource-hierarchy
#   description: Google Cloud Resource Hierarchy Documentation
# - ref: https://cloud.google.com/vpc-service-controls/docs
#   description: VPC Service Controls Documentation
# - ref: https://cloud.google.com/iam/docs
#   description: Google Cloud IAM Documentation
# - ref: https://cloud.google.com/iam/docs/groups-in-gcp
#   description: IAM Groups Documentation
#
# custom:
#   control_id: CIS-3.12
#   framework: cis
#   benchmark: gcp-foundations
#   version: v2.0.0
#   safeguard: 3.12
#   severity: high
#   service: Resource Manager / VPC Service Controls / IAM
#   asset_type: Data
#   implementation_group: 2
#   requires_permissions:
#   - resourcemanager.folders.get
#   - resourcemanager.projects.get
#   - resourcemanager.projects.list
#   - cloudasset.assets.list
#   - accesscontextmanager.accessPolicies.get
#   - accesscontextmanager.servicePerimeters.get
#   - iam.roles.get
#   - iam.serviceAccounts.get
#   - logging.viewer

package cis.gcp_foundations.v2_0_0.control_3_12

import rego.v1

# ---------------------------
# Default Result
# ---------------------------
default result := {
  "compliant": false,
  "message": "Evaluation failed: insufficient data sensitivity segmentation evidence",
  "details": {}
}

default compliant := false

# ---------------------------
# Compliance Logic
# ---------------------------
compliant if {
  input.sensitivity_tiers_defined == true
  input.resource_hierarchy_separated == true
  input.resources_assigned_to_tiers == true
  input.network_boundaries_enforced == true
  input.iam_tier_separation_enabled == true
  input.cross_tier_access_controlled == true
  input.cross_tier_access_audited == true
  valid_tier_definitions
  valid_resource_tiering
  valid_iam_separation
  valid_cross_tier_access
}

# ---------------------------
# Validate Sensitivity Tiers
# ---------------------------
valid_tier_definitions if {
  some tier in input.sensitivity_tiers

  tier.name != ""
  tier.sensitivity_level != ""
  tier.description != ""
  tier.allowed_resources != ""
}

# ---------------------------
# Validate Resource Tiering
# ---------------------------
valid_resource_tiering if {
  some resource in input.tiered_resources

  resource.resource_name != ""
  resource.resource_type != ""
  resource.project_id != ""
  resource.sensitivity_tier != ""
  resource.tier_boundary != ""
}

# ---------------------------
# Validate IAM Tier Separation
# ---------------------------
valid_iam_separation if {
  some tier_access in input.tier_iam_access

  tier_access.sensitivity_tier != ""
  tier_access.group != ""
  tier_access.role != ""
  tier_access.privileged_access_controlled == true
  tier_access.cross_tier_principal_restricted == true
}

# ---------------------------
# Validate Cross-Tier Access
# ---------------------------
valid_cross_tier_access if {
  some pathway in input.cross_tier_access_paths

  pathway.source_tier != ""
  pathway.destination_tier != ""
  pathway.mechanism != ""
  pathway.approval_id != ""
  pathway.approval_timestamp != ""
  pathway.audit_log_matched == true
}

# ---------------------------
# Result Output
# ---------------------------
result := output if {
  resources := get_array(input, "tiered_resources")
  tiers := get_array(input, "sensitivity_tiers")
  perimeters := get_array(input, "service_perimeters")
  cross_tier_paths := get_array(input, "cross_tier_access_paths")

  output := {
    "compliant": compliant,
    "message": generate_message,
    "affected_resources": resources,
    "details": {
      "sensitivity_tiers_defined":
          input.sensitivity_tiers_defined,
      "resource_hierarchy_separated":
          input.resource_hierarchy_separated,
      "resources_assigned_to_tiers":
          input.resources_assigned_to_tiers,
      "network_boundaries_enforced":
          input.network_boundaries_enforced,
      "iam_tier_separation_enabled":
          input.iam_tier_separation_enabled,
      "cross_tier_access_controlled":
          input.cross_tier_access_controlled,
      "cross_tier_access_audited":
          input.cross_tier_access_audited,
      "sensitivity_tier_count":
          count(tiers),
      "tiered_resource_count":
          count(resources),
      "service_perimeter_count":
          count(perimeters),
      "cross_tier_access_path_count":
          count(cross_tier_paths),
      "requires_example_evidence": true
    }
  }
}

# ---------------------------
# Message Logic
# ---------------------------
generate_message := msg if {
  not input.sensitivity_tiers_defined
  msg := "FAIL: Data sensitivity tiers are not defined"
}

generate_message := msg if {
  input.sensitivity_tiers_defined
  not valid_tier_definitions
  msg := "INCONCLUSIVE: Sensitivity tiers exist but tier definitions or permitted resource boundaries are incomplete"
}

generate_message := msg if {
  valid_tier_definitions
  not input.resource_hierarchy_separated
  msg := "FAIL: GCP folders or projects are not separated according to data sensitivity"
}

generate_message := msg if {
  input.resource_hierarchy_separated
  not input.resources_assigned_to_tiers
  msg := "FAIL: In-scope data resources are not assigned to defined sensitivity tiers"
}

generate_message := msg if {
  input.resources_assigned_to_tiers
  not valid_resource_tiering
  msg := "INCONCLUSIVE: Resource tiering is claimed but resource identifiers or tier boundary mappings are incomplete"
}

generate_message := msg if {
  valid_resource_tiering
  not input.network_boundaries_enforced
  msg := "FAIL: Network or service boundaries are not enforced for sensitive data tiers"
}

generate_message := msg if {
  input.network_boundaries_enforced
  not input.iam_tier_separation_enabled
  msg := "FAIL: IAM groups and roles are not separated according to data sensitivity tiers"
}

generate_message := msg if {
  input.iam_tier_separation_enabled
  not valid_iam_separation
  msg := "FAIL: Tier-specific IAM evidence does not demonstrate privileged access controls or restricted cross-tier principals"
}

generate_message := msg if {
  valid_iam_separation
  not input.cross_tier_access_controlled
  msg := "FAIL: Cross-tier access pathways are not explicitly controlled and approved"
}

generate_message := msg if {
  input.cross_tier_access_controlled
  not valid_cross_tier_access
  msg := "INCONCLUSIVE: Cross-tier access exists but approval, mechanism, or audit evidence is incomplete"
}

generate_message := msg if {
  valid_cross_tier_access
  not input.cross_tier_access_audited
  msg := "FAIL: Cross-tier access is not supported by auditable evidence"
}

generate_message := msg if {
  input.cross_tier_access_audited
  not compliant
  msg := "INCONCLUSIVE: Data sensitivity segmentation exists but boundaries, IAM separation, or cross-tier access evidence could not be fully verified"
}

generate_message := msg if {
  compliant
  msg := "PASS: Sensitive GCP data is segmented by sensitivity through resource hierarchy, network boundaries, IAM separation, and explicitly controlled and auditable cross-tier access"
}

# ---------------------------
# Helper Functions
# ---------------------------
get_array(obj, key) := value if {
  value := obj[key]
} else := []
