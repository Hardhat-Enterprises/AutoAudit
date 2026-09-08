# METADATA
# title: Use DHCP Logging to Update Enterprise Asset Inventory (GCP)
# description: |
#   DHCP logging or equivalent IP assignment logging must be used to update
#   the enterprise asset inventory. Logs must be reviewed weekly or more
#   frequently, and inventory updates must be evidenced.
#
#   Google Cloud implementation:
#   - Cloud Logging for DHCP/IPAM logs
#   - Ops Agent for self-managed DHCP servers
#   - BigQuery scheduled queries or automated exports
#   - Cloud Operations for monitoring and alerting
#   - Alternative documented process when DHCP is fully managed by GCP
#
#   The control verifies:
#   - DHCP/IPAM sources are identified
#   - DHCP logs are ingested into Cloud Logging
#   - Weekly reporting schedule exists
#   - Weekly execution is verified
#   - Inventory updates are evidenced
#   - GCP-managed DHCP environments have an approved alternative process
#
# related_resources:
# - ref: https://cloud.google.com/logging/docs
#   description: Cloud Logging Documentation
# - ref: https://cloud.google.com/monitoring
#   description: Cloud Monitoring Documentation
# - ref: https://cloud.google.com/compute/docs/manage-os
#   description: Ops Agent Documentation
# - ref: https://cloud.google.com/bigquery/docs/scheduling-queries
#   description: BigQuery Scheduled Queries
#
# custom:
#   control_id: CIS-1.4
#   framework: cis
#   benchmark: gcp-foundations
#   version: v2.0.0
#   safeguard: 1.4
#   severity: medium
#   service: Cloud Logging
#   asset_type: Devices
#   implementation_group: 2
#   requires_permissions:
#   - logging.viewer
#   - monitoring.viewer
#   - bigquery.jobs.list
#   - compute.viewer

package cis.gcp_foundations.v2_0_0.control_1_4

import rego.v1

# ---------------------------
# Default Result
# ---------------------------
default compliant := false

default result := {
    "compliant": false,
    "message": "Evaluation failed: insufficient DHCP logging evidence",
    "details": {}
}

# ---------------------------
# Compliance Logic
# ---------------------------
compliant if {
    input.dhcp_sources_identified == true
    input.logging_ingestion_enabled == true
    input.weekly_reporting_schedule_defined == true
    reporting_execution_verified
    inventory_update_verified
    alternative_process_verified
}

# ---------------------------
# Weekly Reporting Validation
# ---------------------------
reporting_execution_verified if {
    input.reporting_frequency_days <= 7
    input.last_report_timestamp != ""
    input.scheduler_last_run_status == "SUCCESS"
}

# ---------------------------
# Inventory Update Validation
# ---------------------------
inventory_update_verified if {

    updates := get_array(input, "inventory_updates")

    count(updates) > 0

    every update in updates {
        update.asset_id != ""
        update.change_ticket != ""
        update.timestamp != ""
    }
}

# ---------------------------
# Alternative Process Validation
# ---------------------------
# If DHCP is self-managed, no alternative process is required.
# If DHCP is GCP-managed, an approved alternative IP assignment
# review process must exist.

alternative_process_verified if {
    input.gcp_managed_dhcp == false
}

alternative_process_verified if {
    input.gcp_managed_dhcp == true
    input.alternative_process_documented == true
}

# ---------------------------
# Result
# ---------------------------
result := output if {

    updates := get_array(input, "inventory_updates")

    output := {
        "compliant": compliant,
        "message": generate_message,
        "affected_resources": updates,
        "details": {
            "dhcp_sources_identified": input.dhcp_sources_identified,
            "logging_ingestion_enabled": input.logging_ingestion_enabled,
            "gcp_managed_dhcp": input.gcp_managed_dhcp,
            "alternative_process_documented": input.alternative_process_documented,
            "reporting_frequency_days": input.reporting_frequency_days,
            "last_report_timestamp": input.last_report_timestamp,
            "scheduler_last_run_status": input.scheduler_last_run_status,
            "inventory_update_count": count(updates),
            "requires_sample_evidence": true
        }
    }
}

# ---------------------------
# Message Logic
# ---------------------------
generate_message := msg if {
    not input.dhcp_sources_identified
    msg := "FAIL: DHCP/IPAM sources are not identified"
}

generate_message := msg if {
    input.dhcp_sources_identified
    not input.logging_ingestion_enabled
    msg := "FAIL: DHCP/IPAM logs are not being ingested into Cloud Logging"
}

generate_message := msg if {
    input.logging_ingestion_enabled
    not input.weekly_reporting_schedule_defined
    msg := "FAIL: No scheduled weekly DHCP reporting process exists"
}

generate_message := msg if {
    input.weekly_reporting_schedule_defined
    not reporting_execution_verified
    msg := "FAIL: Weekly reporting schedule exists but execution evidence is missing or unsuccessful"
}

generate_message := msg if {
    reporting_execution_verified
    input.gcp_managed_dhcp
    not input.alternative_process_documented
    msg := "FAIL: GCP-managed DHCP requires a documented alternative IP assignment review process"
}

generate_message := msg if {
    alternative_process_verified
    not inventory_update_verified
    msg := "INCONCLUSIVE: DHCP reporting exists but inventory update evidence is missing"
}

generate_message := msg if {
    compliant
    msg := "PASS: DHCP/IP assignment logging is reviewed weekly and used to maintain the enterprise asset inventory"
}

# ---------------------------
# Helper Function
# ---------------------------
get_array(obj, key) := value if {
    value := obj[key]
} else := []