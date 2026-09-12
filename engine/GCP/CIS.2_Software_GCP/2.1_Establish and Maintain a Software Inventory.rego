# METADATA
# title: Establish and Maintain a Software Inventory (GCP)
# description: |
#   A detailed inventory of licensed software installed on enterprise assets
#   must be established and maintained. The inventory must include required
#   software metadata and be reviewed at least every six months.
#
#   Google Cloud implementation uses:
#   - Cloud Asset Inventory (CAI) to enumerate compute resources
#   - OS Config / VM Manager OS Inventory for installed software/packages
#   - Artifact Registry for container image inventory
#   - BigQuery or CMDB scheduled exports for inventory refresh
#
#   The control verifies:
#   - Software inventory exists
#   - Inventory scope is defined
#   - Required software metadata is present
#   - Container inventory is included where applicable
#   - Inventory review schedule exists
#   - Inventory refresh execution is verified
#
# related_resources:
# - ref: https://cloud.google.com/compute/vm-manager/docs/os-inventory
#   description: VM Manager OS Inventory Documentation
# - ref: https://cloud.google.com/asset-inventory/docs
#   description: Cloud Asset Inventory Documentation
# - ref: https://cloud.google.com/artifact-registry/docs
#   description: Artifact Registry Documentation
# - ref: https://cloud.google.com/bigquery/docs/scheduling-queries
#   description: BigQuery Scheduled Queries
#
# custom:
#   control_id: CIS-2.1
#   framework: cis
#   benchmark: gcp-foundations
#   version: v2.0.0
#   safeguard: 2.1
#   severity: high
#   service: VM Manager
#   asset_type: Software
#   implementation_group: 1
#   requires_permissions:
#   - osconfig.inventoryViewer
#   - cloudasset.viewer
#   - artifactregistry.reader

package cis.gcp_foundations.v2_0_0.control_2_1

import rego.v1

# ---------------------------
# Default Result
# ---------------------------
default compliant := false

default result := {
    "compliant": false,
    "message": "Evaluation failed: insufficient software inventory evidence",
    "details": {}
}

# ---------------------------
# Compliance Logic
# ---------------------------
compliant if {
    input.software_inventory_available == true
    input.inventory_scope_defined == true
    required_metadata_present
    container_inventory_verified
    input.review_schedule_defined == true
    review_execution_verified
}

# ---------------------------
# Validate Software Metadata
# ---------------------------
required_metadata_present if {
    every software in input.software_inventory {
        software.title != ""
        software.publisher != ""
        software.version != ""
        software.install_date != ""
        software.asset_id != ""
        software.project_id != ""
        software.business_purpose != ""
    }
}

# ---------------------------
# Validate Container Inventory
# ---------------------------
container_inventory_verified if {
    input.containers_in_scope == false
}

container_inventory_verified if {
    input.containers_in_scope == true

    every image in input.container_inventory {
        image.repository != ""
        image.image_digest != ""
        image.tag != ""
        image.created_time != ""
    }
}

# ---------------------------
# Validate Review Evidence
# ---------------------------
review_execution_verified if {
    input.review_frequency_days <= 183
    input.last_review_timestamp != ""
    input.scheduler_last_run_status == "SUCCESS"
}

# ---------------------------
# Result Output
# ---------------------------
result := output if {

    software := get_array(input, "software_inventory")
    images := get_array(input, "container_inventory")

    output := {
        "compliant": compliant,
        "message": generate_message,
        "affected_resources": software,
        "details": {
            "inventory_scope": input.inventory_scope,
            "software_inventory_available": input.software_inventory_available,
            "software_count": count(software),
            "containers_in_scope": input.containers_in_scope,
            "container_image_count": count(images),
            "review_frequency_days": input.review_frequency_days,
            "last_review_timestamp": input.last_review_timestamp,
            "scheduler_last_run_status": input.scheduler_last_run_status,
            "requires_sample_evidence": true
        }
    }
}

# ---------------------------
# Message Logic
# ---------------------------
generate_message := msg if {
    not input.software_inventory_available
    msg := "FAIL: Software inventory is not available"
}

generate_message := msg if {
    input.software_inventory_available
    not input.inventory_scope_defined
    msg := "FAIL: Software inventory scope is not defined"
}

generate_message := msg if {
    input.inventory_scope_defined
    not required_metadata_present
    msg := "FAIL: Software inventory is missing required metadata fields"
}

generate_message := msg if {
    required_metadata_present
    not container_inventory_verified
    msg := "FAIL: Container image inventory is incomplete for the defined scope"
}

generate_message := msg if {
    container_inventory_verified
    not input.review_schedule_defined
    msg := "FAIL: No evidence of a software inventory review schedule"
}

generate_message := msg if {
    input.review_schedule_defined
    not review_execution_verified
    msg := "INCONCLUSIVE: Inventory review schedule exists but execution evidence is missing"
}

generate_message := msg if {
    compliant
    msg := "PASS: Software inventory is established, maintained, and reviewed at least bi-annually"
}

# ---------------------------
# Helper Functions
# ---------------------------
get_array(obj, key) := value if {
    value := obj[key]
} else := []