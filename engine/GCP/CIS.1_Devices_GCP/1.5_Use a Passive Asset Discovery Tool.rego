# METADATA
# title: Use a Passive Asset Discovery Tool (GCP Packet Mirroring / VPC Flow Logs)
# description: |
#   Passive network telemetry must be used to identify assets connected to
#   the enterprise network. Discovered endpoints must be reviewed at least
#   weekly and used to update the enterprise asset inventory.
#
#   Google Cloud implementation:
#   - Security Command Center (asset context)
#   - Packet Mirroring
#   - Cloud Logging
#   - BigQuery / SIEM
#   - VPC Flow Logs (approved alternative where Packet Mirroring is not deployed)
#
#   The control verifies:
#   - Passive telemetry is enabled
#   - Discovery scope is defined
#   - Endpoint telemetry is collected
#   - Weekly review schedule exists
#   - Weekly review execution is verified
#   - New/unknown endpoints are triaged
#   - Sample remediation or approved exceptions exist
#
# related_resources:
# - ref: https://cloud.google.com/vpc/docs/packet-mirroring
#   description: Packet Mirroring Documentation
# - ref: https://cloud.google.com/vpc/docs/flow-logs
#   description: VPC Flow Logs Documentation
# - ref: https://cloud.google.com/security-command-center/docs
#   description: Security Command Center Documentation
# - ref: https://cloud.google.com/logging/docs
#   description: Cloud Logging Documentation
# - ref: https://cloud.google.com/bigquery/docs/scheduling-queries
#   description: BigQuery Scheduled Queries
#
# custom:
#   control_id: CIS-1.5
#   framework: cis
#   benchmark: gcp-foundations
#   version: v2.0.0
#   safeguard: 1.5
#   severity: high
#   service: Packet Mirroring
#   asset_type: Devices
#   implementation_group: 3
#   requires_permissions:
#   - compute.packetMirrorings.list
#   - logging.viewer
#   - securitycenter.assets.list
#   - bigquery.jobs.list

package cis.gcp_foundations.v2_0_0.control_1_5

import rego.v1

# ---------------------------
# Default Result
# ---------------------------
default compliant := false

default result := {
    "compliant": false,
    "message": "Evaluation failed: insufficient passive asset discovery evidence",
    "details": {}
}

# ---------------------------
# Compliance Logic
# ---------------------------
compliant if {
    input.discovery_scope_defined == true
    passive_telemetry_enabled
    endpoint_collection_verified
    input.weekly_review_schedule_defined == true
    weekly_review_verified
    triage_verified
    remediation_verified
}

# ---------------------------
# Passive Telemetry Validation
# ---------------------------
# Either Packet Mirroring or VPC Flow Logs
# satisfies the passive discovery requirement.

passive_telemetry_enabled if {
    input.packet_mirroring_enabled == true
}

passive_telemetry_enabled if {
    input.packet_mirroring_enabled == false
    input.vpc_flow_logs_enabled == true
}

# ---------------------------
# Endpoint Collection Validation
# ---------------------------
endpoint_collection_verified if {

    endpoints := get_array(input, "observed_endpoints")

    count(endpoints) > 0

    every endpoint in endpoints {
        endpoint.source_ip != ""
        endpoint.destination_ip != ""
        endpoint.timestamp != ""
    }
}

# ---------------------------
# Weekly Review Validation
# ---------------------------
weekly_review_verified if {
    input.review_frequency_days <= 7
    input.last_review_timestamp != ""
    input.scheduler_last_run_status == "SUCCESS"
}

# ---------------------------
# Triage Validation
# ---------------------------
triage_verified if {

    tickets := get_array(input, "triage_tickets")

    count(tickets) > 0

    every ticket in tickets {
        ticket.id != ""
        ticket.status != ""
        ticket.created_timestamp != ""
    }
}

# ---------------------------
# Remediation / Exception Validation
# ---------------------------
remediation_verified if {

    actions := get_array(input, "remediation_actions")

    count(actions) > 0

    every action in actions {
        action.asset_id != ""
        action.status != ""
        action.timestamp != ""
    }
}

remediation_verified if {

    exceptions := get_array(input, "approved_exceptions")

    count(exceptions) > 0

    every exception in exceptions {
        exception.asset_id != ""
        exception.approval_id != ""
        exception.expiry_date != ""
    }
}

# ---------------------------
# Result
# ---------------------------
result := output if {

    endpoints := get_array(input, "observed_endpoints")
    tickets := get_array(input, "triage_tickets")

    output := {
        "compliant": compliant,
        "message": generate_message,
        "affected_resources": endpoints,
        "details": {
            "packet_mirroring_enabled": input.packet_mirroring_enabled,
            "vpc_flow_logs_enabled": input.vpc_flow_logs_enabled,
            "discovery_scope": input.discovery_scope,
            "review_frequency_days": input.review_frequency_days,
            "last_review_timestamp": input.last_review_timestamp,
            "scheduler_last_run_status": input.scheduler_last_run_status,
            "endpoint_count": count(endpoints),
            "ticket_count": count(tickets),
            "requires_sample_evidence": true
        }
    }
}

# ---------------------------
# Message Logic
# ---------------------------
generate_message := msg if {
    not input.discovery_scope_defined
    msg := "FAIL: Passive discovery scope is not defined"
}

generate_message := msg if {
    input.discovery_scope_defined
    not passive_telemetry_enabled
    msg := "FAIL: Neither Packet Mirroring nor VPC Flow Logs are enabled for the defined scope"
}

generate_message := msg if {
    passive_telemetry_enabled
    not endpoint_collection_verified
    msg := "FAIL: No passive endpoint discovery evidence was provided"
}

generate_message := msg if {
    endpoint_collection_verified
    not input.weekly_review_schedule_defined
    msg := "FAIL: No scheduled weekly review process exists"
}

generate_message := msg if {
    input.weekly_review_schedule_defined
    not weekly_review_verified
    msg := "FAIL: Weekly review schedule exists but execution evidence is missing or unsuccessful"
}

generate_message := msg if {
    weekly_review_verified
    not triage_verified
    msg := "FAIL: Newly discovered endpoints are not triaged"
}

generate_message := msg if {
    triage_verified
    not remediation_verified
    msg := "FAIL: No remediation actions or approved exceptions were provided"
}

generate_message := msg if {
    compliant
    msg := "PASS: Passive asset discovery is performed, reviewed weekly, and supported by triage and remediation evidence"
}

# ---------------------------
# Helper Function
# ---------------------------
get_array(obj, key) := value if {
    value := obj[key]
} else := []
