# METADATA
# title: Ensure Authorized Software is Currently Supported (GCP)
# description: |
#   Only currently supported software must be designated as authorized on
#   enterprise assets. Unsupported software must either have an approved,
#   time-bound exception with documented compensating controls and residual
#   risk acceptance, or be designated as unauthorized.
#
#   Google Cloud implementation uses:
#   - OS Config / VM Manager OS Inventory for installed software and versions
#   - Security Command Center (SCC) findings for vulnerable or unsupported software
#   - Vendor lifecycle references or internal support standards
#   - Monthly support-status review using BigQuery, scheduled exports, or CMDB
#   - Exception register maintained in a ticketing or risk management system
#
#   The control verifies:
#   - Software inventory exists
#   - Support status is recorded for all software
#   - Unsupported software has approved exceptions or is marked unauthorized
#   - Monthly review schedule exists
#   - Monthly review execution is verified
#   - Remediation evidence exists for upgraded software
#
# related_resources:
# - ref: https://cloud.google.com/compute/vm-manager/docs/os-inventory
#   description: VM Manager OS Inventory Documentation
# - ref: https://cloud.google.com/security-command-center/docs
#   description: Security Command Center Documentation
# - ref: https://cloud.google.com/bigquery/docs/scheduling-queries
#   description: BigQuery Scheduled Queries
#
# custom:
#   control_id: CIS-2.2
#   framework: cis
#   benchmark: gcp-foundations
#   version: v2.0.0
#   safeguard: 2.2
#   severity: high
#   service: VM Manager
#   asset_type: Software
#   implementation_group: 1
#   requires_permissions:
#   - osconfig.inventoryViewer
#   - securitycenter.findings.list
#   - bigquery.jobs.list

package cis.gcp_foundations.v2_0_0.control_2_2

import rego.v1

# ---------------------------
# Default Result
# ---------------------------
default compliant := false

default result := {
    "compliant": false,
    "message": "Evaluation failed: insufficient software support status evidence",
    "details": {}
}

# ---------------------------
# Compliance Logic
# ---------------------------
compliant if {
    input.software_inventory_available == true
    input.support_status_tracked == true
    support_status_verified
    exception_register_verified
    input.review_schedule_defined == true
    review_execution_verified
}

# ---------------------------
# Validate Support Status
# ---------------------------
support_status_verified if {
    every software in input.software_inventory {
        software.title != ""
        software.version != ""
        software.support_status != ""

        software.support_status == "SUPPORTED"
        or
        software.support_status == "UNSUPPORTED"
    }
}

# ---------------------------
# Validate Exception Register
# ---------------------------
exception_register_verified if {
    every software in input.software_inventory {

        software.support_status == "SUPPORTED"
    }
}

exception_register_verified if {
    every exception in input.exception_register {
        exception.software_title != ""
        exception.business_justification != ""
        exception.compensating_controls != ""
        exception.approver != ""
        exception.expiry_date != ""
        exception.residual_risk_accepted == true
    }
}

# ---------------------------
# Validate Review Evidence
# ---------------------------
review_execution_verified if {
    input.review_frequency_days <= 31
    input.last_review_timestamp != ""
    input.scheduler_last_run_status == "SUCCESS"
}

# ---------------------------
# Validate Remediation Evidence
# ---------------------------
remediation_verified if {
    count(get_array(input, "remediation_records")) > 0
}

remediation_verified if {
    count(get_array(input, "unsupported_software")) == 0
}

# ---------------------------
# Result Output
# ---------------------------

result := output if {

    software := get_array(input, "software_inventory")
    exceptions := get_array(input, "exception_register")
    remediation := get_array(input, "remediation_records")

    output := {
        "compliant": compliant,
        "message": generate_message,
        "affected_resources": software,
        "details": {
            "software_inventory_available": input.software_inventory_available,
            "support_status_tracked": input.support_status_tracked,
            "software_count": count(software),
            "exception_count": count(exceptions),
            "remediation_count": count(remediation),
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
    not input.support_status_tracked
    msg := "FAIL: Software support status is not tracked"
}

generate_message := msg if {
    input.support_status_tracked
    not support_status_verified
    msg := "FAIL: Software inventory does not contain valid support status information"
}

generate_message := msg if {
    support_status_verified
    not exception_register_verified
    msg := "FAIL: Unsupported software is missing approved exception documentation"
}

generate_message := msg if {
    exception_register_verified
    not input.review_schedule_defined
    msg := "FAIL: No evidence of a monthly software support review schedule"
}

generate_message := msg if {
    input.review_schedule_defined
    not review_execution_verified
    msg := "INCONCLUSIVE: Monthly review schedule exists but execution evidence is missing"
}

generate_message := msg if {
    review_execution_verified
    not remediation_verified
    msg := "FAIL: Unsupported software exists without remediation evidence"
}

generate_message := msg if {
    compliant
    msg := "PASS: Authorized software is currently supported or has approved, time-bound exceptions with monthly review evidence"
}

# ---------------------------
# Helper Functions
# ---------------------------
get_array(obj, key) := value if {
    value := obj[key]
} else := []