# METADATA
# title: Utilize an Active Discovery Tool (GCP SCC + VPC Flow Logs)
# description: |
#   Assets connected to the enterprise network must be actively discovered
#   using automated discovery mechanisms. Discovery must execute daily or
#   more frequently and produce evidence of observed endpoints.
#
#   Google Cloud implementation uses:
#   - Security Command Center (SCC) Assets View
#   - VPC Flow Logs
#   - BigQuery scheduled queries or equivalent automation
#   - Optional log-based metrics and alerting
#
#   The control verifies:
#   - SCC Assets view is enabled
#   - VPC Flow Logs are enabled
#   - Discovery scope is defined
#   - Daily discovery schedule exists
#   - Daily execution is verified
#   - Discovery output identifies observed endpoints
#   - Optional alerting configuration
#
# related_resources:
# - ref: https://cloud.google.com/security-command-center/docs
#   description: Security Command Center Documentation
# - ref: https://cloud.google.com/vpc/docs/flow-logs
#   description: VPC Flow Logs Documentation
# - ref: https://cloud.google.com/bigquery/docs/scheduling-queries
#   description: BigQuery Scheduled Queries
# - ref: https://cloud.google.com/logging/docs/logs-based-metrics
#   description: Cloud Logging Metrics
#
# custom:
#   control_id: CIS-1.3
#   framework: cis
#   benchmark: gcp-foundations
#   version: v2.0.0
#   safeguard: 1.3
#   severity: high
#   service: Security Command Center
#   asset_type: Devices
#   implementation_group: 2
#   requires_permissions:
#   - securitycenter.assets.list
#   - logging.configViewer
#   - compute.networkViewer
#   - bigquery.jobs.list

package cis.gcp_foundations.v2_0_0.control_1_3

import rego.v1

# ---------------------------
# Default Result
# ---------------------------
default compliant := false

default result := {
    "compliant": false,
    "message": "Evaluation failed: insufficient evidence of active asset discovery",
    "details": {}
}

# ---------------------------
# Compliance Logic
# ---------------------------
compliant if {
    input.scc_enabled == true
    input.scc_assets_populated == true
    input.discovery_scope_defined == true
    input.vpc_flow_logs_enabled == true
    input.discovery_schedule_defined == true
    discovery_execution_verified
    discovery_output_verified
}

# ---------------------------
# Discovery Execution Validation
# ---------------------------
discovery_execution_verified if {
    input.discovery_frequency_days <= 1
    input.last_discovery_run_timestamp != ""
    input.scheduler_last_run_status == "SUCCESS"
}

# ---------------------------
# Discovery Output Validation
# ---------------------------
discovery_output_verified if {

    endpoints := get_array(input, "observed_endpoints")

    count(endpoints) > 0

    every endpoint in endpoints {
        endpoint.source_ip != ""
        endpoint.destination_ip != ""
        endpoint.timestamp != ""
    }
}

# ---------------------------
# Result Output
# ---------------------------
result := output if {

    endpoints := get_array(input, "observed_endpoints")

    output := {
        "compliant": compliant,
        "message": generate_message,
        "affected_resources": endpoints,
        "details": {
            "scc_enabled": input.scc_enabled,
            "scc_assets_populated": input.scc_assets_populated,
            "vpc_flow_logs_enabled": input.vpc_flow_logs_enabled,
            "discovery_scope": input.discovery_scope,
            "discovery_frequency_days": input.discovery_frequency_days,
            "last_discovery_run": input.last_discovery_run_timestamp,
            "scheduler_last_run_status": input.scheduler_last_run_status,
            "endpoint_count": count(endpoints),
            "alerting_enabled": input.log_alerting_enabled,
            "requires_sample_evidence": true
        }
    }
}

# ---------------------------
# Message Logic
# ---------------------------
generate_message := msg if {
    not input.scc_enabled
    msg := "FAIL: Security Command Center is not enabled"
}

generate_message := msg if {
    input.scc_enabled
    not input.scc_assets_populated
    msg := "FAIL: SCC Assets view is not populated"
}

generate_message := msg if {
    input.scc_assets_populated
    not input.discovery_scope_defined
    msg := "FAIL: Discovery scope is not defined"
}

generate_message := msg if {
    input.discovery_scope_defined
    not input.vpc_flow_logs_enabled
    msg := "FAIL: VPC Flow Logs are not enabled for the defined scope"
}

generate_message := msg if {
    input.vpc_flow_logs_enabled
    not input.discovery_schedule_defined
    msg := "FAIL: No scheduled daily discovery job exists"
}

generate_message := msg if {
    input.discovery_schedule_defined
    not discovery_execution_verified
    msg := "FAIL: Discovery schedule exists but execution evidence is missing or unsuccessful"
}

generate_message := msg if {
    discovery_execution_verified
    not discovery_output_verified
    msg := "INCONCLUSIVE: Discovery job exists but discovery output or endpoint evidence is missing"
}

generate_message := msg if {
    compliant
    msg := "PASS: Active asset discovery is performed daily using SCC Assets and VPC Flow Logs"
}

# ---------------------------
# Helper Function
# ---------------------------
get_array(obj, key) := value if {
    value := obj[key]
} else := []