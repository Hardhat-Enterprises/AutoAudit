# METADATA
# title: Utilize Automated Software Inventory Tools (GCP)
# description: |
#   Software inventory tools must be used to automatically discover and
#   document installed software across enterprise assets wherever possible.
#
#   Google Cloud implementation uses:
#   - Cloud Asset Inventory (CAI) to define the in-scope compute population
#   - OS Config / VM Manager agents to automatically collect software inventory
#   - BigQuery or Cloud Storage exports for centralized inventory reporting
#   - Cloud Logging for export automation and monitoring
#
#   The control verifies:
#   - Software inventory automation is enabled
#   - Agent coverage exists across the defined scope
#   - Central inventory export is configured
#   - Automated inventory execution is verified
#   - Exception handling exists for unmanaged assets
#
# related_resources:
# - ref: https://cloud.google.com/compute/vm-manager/docs/os-inventory
#   description: VM Manager OS Inventory Documentation
# - ref: https://cloud.google.com/asset-inventory/docs
#   description: Cloud Asset Inventory Documentation
# - ref: https://cloud.google.com/bigquery/docs/scheduling-queries
#   description: BigQuery Scheduled Queries
# - ref: https://cloud.google.com/logging/docs
#   description: Cloud Logging Documentation
#
# custom:
#   control_id: CIS-2.4
#   framework: cis
#   benchmark: gcp-foundations
#   version: v2.0.0
#   safeguard: 2.4
#   severity: medium
#   service: VM Manager
#   asset_type: Software
#   implementation_group: 2
#   requires_permissions:
#   - osconfig.inventoryViewer
#   - cloudasset.viewer
#   - bigquery.jobs.list
#   - logging.viewer

package cis.gcp_foundations.v2_0_0.control_2_4

import rego.v1

# ---------------------------
# Default Result
# ---------------------------
default compliant := false

default result := {
    "compliant": false,
    "message": "Evaluation failed: insufficient automated software inventory evidence",
    "details": {}
}

# ---------------------------
# Compliance Logic
# ---------------------------
compliant if {
    input.inventory_automation_enabled == true
    input.inventory_scope_defined == true
    agent_coverage_verified
    export_configuration_verified
    inventory_execution_verified
    unmanaged_assets_verified
}

# ---------------------------
# Validate Agent Coverage
# ---------------------------
agent_coverage_verified if {
    every agent in input.agent_coverage {
        agent.asset_id != ""
        agent.status == "ACTIVE"
        agent.last_checkin != ""
    }
}

# ---------------------------
# Validate Export Configuration
# ---------------------------
export_configuration_verified if {
    input.central_export_enabled == true
    input.export_destination != ""
}

# ---------------------------
# Validate Inventory Execution
# ---------------------------
inventory_execution_verified if {
    input.last_inventory_timestamp != ""
    input.scheduler_last_run_status == "SUCCESS"
    input.export_frequency_days <= 31
}

# ---------------------------
# Validate Unmanaged Assets
# ---------------------------
unmanaged_assets_verified if {
    count(get_array(input, "unmanaged_assets")) == 0
}

unmanaged_assets_verified if {
    every asset in input.unmanaged_assets {
        asset.asset_id != ""
        asset.reason != ""
        asset.approved_exception == true
    }
}

# ---------------------------
# Result Output
# ---------------------------
result := output if {

    agents := get_array(input, "agent_coverage")
    unmanaged := get_array(input, "unmanaged_assets")

    output := {
        "compliant": compliant,
        "message": generate_message,
        "affected_resources": agents,
        "details": {
            "inventory_automation_enabled": input.inventory_automation_enabled,
            "inventory_scope": input.inventory_scope,
            "agent_count": count(agents),
            "central_export_enabled": input.central_export_enabled,
            "export_destination": input.export_destination,
            "export_frequency_days": input.export_frequency_days,
            "last_inventory_timestamp": input.last_inventory_timestamp,
            "scheduler_last_run_status": input.scheduler_last_run_status,
            "unmanaged_asset_count": count(unmanaged),
            "requires_sample_evidence": true
        }
    }
}

# ---------------------------
# Message Logic
# ---------------------------
generate_message := msg if {
    not input.inventory_automation_enabled
    msg := "FAIL: Automated software inventory is not enabled"
}

generate_message := msg if {
    input.inventory_automation_enabled
    not input.inventory_scope_defined
    msg := "FAIL: Automated software inventory scope is not defined"
}

generate_message := msg if {
    input.inventory_scope_defined
    not agent_coverage_verified
    msg := "FAIL: VM Manager or OS Config agent coverage is incomplete"
}

generate_message := msg if {
    agent_coverage_verified
    not export_configuration_verified
    msg := "FAIL: Centralized inventory export is not configured"
}

generate_message := msg if {
    export_configuration_verified
    not inventory_execution_verified
    msg := "INCONCLUSIVE: Automated inventory is configured but recurring execution cannot be verified"
}

generate_message := msg if {
    inventory_execution_verified
    not unmanaged_assets_verified
    msg := "FAIL: Unmanaged assets are not documented with approved exceptions"
}

generate_message := msg if {
    compliant
    msg := "PASS: Automated software inventory is deployed, centrally collected, and regularly executed across the defined scope"
}

# ---------------------------
# Helper Functions
# ---------------------------
get_array(obj, key) := value if {
    value := obj[key]
} else := []
