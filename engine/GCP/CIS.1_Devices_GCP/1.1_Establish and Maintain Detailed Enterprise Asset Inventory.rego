# METADATA
# title: Establish and Maintain Detailed Enterprise Asset Inventory (GCP CAI)
# description: |
#   Enterprise assets within GCP must be inventoried using Google Cloud Asset Inventory (CAI).
#   The inventory must cover the approved GCP scope (Organization, Folder, or Project),
#   contain required asset metadata, and have evidence of periodic review and updates.
#
#   The control verifies:
#   - CAI inventory exists
#   - Inventory scope is defined
#   - Asset metadata is captured
#   - Inventory export evidence exists
#   - Review/update frequency is enforced
#
# related_resources:
# - ref: https://cloud.google.com/asset-inventory/docs
#   description: Google Cloud Asset Inventory Documentation
# - ref: https://cloud.google.com/scheduler/docs
#   description: Cloud Scheduler Documentation
#
# custom:
#   control_id: CIS-1.1
#   framework: cis
#   benchmark: gcp-foundations
#   version: v2.0.0
#   safeguard: 1.1
#   severity: high
#   service: Cloud Asset Inventory
#   asset_type: Devices
#   implementation_group: 1
#   requires_permissions:
#   - cloudasset.viewer
#   - cloudasset.assets.list

package cis.gcp_foundations.v2_0_0.control_1_1

import rego.v1

# ---------------------------
# Default Result
# ---------------------------

default compliant := false

default result := {
    "compliant": false,
    "message": "Evaluation failed: insufficient Cloud Asset Inventory evidence",
    "details": {}
}

# ---------------------------
# Compliance Logic
# ---------------------------
compliant if {
    input.cai_enabled == true
    input.inventory_scope_defined == true
    input.asset_export_available == true
    required_metadata_present
    input.review_schedule_defined == true
    review_execution_verified
}

# ---------------------------
# Validate Asset Inventory
# ---------------------------
required_metadata_present if {
    assets := object.get(input, "assets", [])
    count(assets) > 0
    every asset in assets {
        is_string(asset.asset_name)
        asset.asset_name != ""
        is_string(asset.asset_type)
        asset.asset_type != ""
        is_string(asset.project_id)
        asset.project_id != ""
        is_string(asset.owner)
        asset.owner != ""
        is_string(asset.network_address)
        asset.network_address != ""
        is_string(asset.approved_connection_status)
        asset.approved_connection_status != ""
    }
}

# ---------------------------
# Validate Review Evidence
# ---------------------------
review_execution_verified if {
    is_number(input.review_frequency_days)
    input.review_frequency_days >= 0
    input.review_frequency_days <= 180
    is_string(input.last_inventory_review_timestamp)
    input.last_inventory_review_timestamp != ""
    input.scheduler_last_run_status == "SUCCESS"
    review_timestamp := time.parse_rfc3339_ns(input.last_inventory_review_timestamp)
    now := time.now_ns()
    cutoff := now - (input.review_frequency_days * 24 * 60 * 60 * 1000000000)
    review_timestamp >= cutoff
    review_timestamp <= now
}

# ---------------------------
# Result Output
# ---------------------------
result := output if {
    assets := object.get(input, "assets", [])
    output := {
        "compliant": compliant,
        "message": generate_message,
        "affected_resources": assets,
        "details": {
            "cai_enabled": object.get(input, "cai_enabled", false),
            "inventory_scope_defined": object.get(input, "inventory_scope_defined", false),
            "inventory_scope": object.get(input, "inventory_scope", ""),
            "asset_export_available": object.get(input, "asset_export_available", false),
            "required_metadata_present": required_metadata_present,
            "asset_count": count(assets),
            "review_schedule_defined": object.get(input, "review_schedule_defined", false),
            "review_frequency_days": object.get(input, "review_frequency_days", null),
            "last_inventory_review_timestamp": object.get(input, "last_inventory_review_timestamp", ""),
            "scheduler_last_run_status": object.get(input, "scheduler_last_run_status", ""),
            "review_execution_verified": review_execution_verified
        }
    }
}

# ---------------------------
# Result Messages
# ---------------------------
generate_message := msg if {
    not input.cai_enabled
    msg := "FAIL: Google Cloud Asset Inventory is not enabled"
}

generate_message := msg if {
    input.cai_enabled
    not input.inventory_scope_defined
    msg := "FAIL: Asset inventory scope is not defined (Org/Folder/Project)"
}

generate_message := msg if {
    input.cai_enabled
    input.inventory_scope_defined
    not input.asset_export_available
    msg := "FAIL: No CAI inventory export evidence provided"
}

generate_message := msg if {
    input.cai_enabled
    input.inventory_scope_defined
    input.asset_export_available
    not required_metadata_present
    msg := "FAIL: Asset inventory does not contain all required metadata"
}

generate_message := msg if {
    input.cai_enabled
    input.inventory_scope_defined
    input.asset_export_available
    required_metadata_present
    not input.review_schedule_defined
    msg := "FAIL: No evidence of periodic inventory review schedule"
}

generate_message := msg if {
    input.cai_enabled
    input.inventory_scope_defined
    input.asset_export_available
    required_metadata_present
    input.review_schedule_defined
    not review_execution_verified
    msg := "INCONCLUSIVE: Review frequency claimed but successful execution evidence is missing or stale"
}

generate_message := msg if {
    compliant
    msg := "PASS: GCP Cloud Asset Inventory is established, maintained, and periodically reviewed"
}
