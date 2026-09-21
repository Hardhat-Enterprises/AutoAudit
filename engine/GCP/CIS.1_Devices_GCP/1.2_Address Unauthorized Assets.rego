# METADATA
# title: Address Unauthorized Assets (GCP SCC / CAI / BeyondCorp)
# description: |
#   Unauthorized assets within the approved GCP scope must be identified and
#   addressed through a documented weekly process.
#
#   Detection should be performed using Security Command Center (SCC) findings
#   and Cloud Asset Inventory (CAI), while remediation may include asset removal,
#   blocking unmanaged devices using BeyondCorp Enterprise / Context-Aware Access,
#   or quarantine through enterprise controls.
#
#   The control verifies:
#   - SCC is enabled and collecting findings
#   - Detection scope is defined
#   - Weekly review schedule exists
#   - Weekly review execution is verified
#   - Findings are triaged through tickets/workflow
#   - Sample remediation evidence exists
#
# related_resources:
# - ref: https://cloud.google.com/security-command-center/docs
#   description: Google Cloud Security Command Center Documentation
# - ref: https://cloud.google.com/asset-inventory/docs
#   description: Cloud Asset Inventory Documentation
# - ref: https://cloud.google.com/beyondcorp-enterprise/docs
#   description: BeyondCorp Enterprise Documentation
# - ref: https://cloud.google.com/access-context-manager/docs
#   description: Context-Aware Access Documentation
#
# custom:
#   control_id: CIS-1.2
#   framework: cis
#   benchmark: gcp-foundations
#   version: v2.0.0
#   safeguard: 1.2
#   severity: high
#   service: Security Command Center
#   asset_type: Devices
#   implementation_group: 1
#   requires_permissions:
#   - securitycenter.findings.list
#   - cloudasset.assets.list
#   - accesscontextmanager.policies.get

package cis.gcp_foundations.v2_0_0.control_1_2

import rego.v1

# ---------------------------
# Default Result
# ---------------------------
default compliant := false

default result := {
    "compliant": false,
    "message": "Evaluation failed: insufficient evidence for unauthorized asset management",
    "details": {}
}

# ---------------------------
# Compliance Logic
# ---------------------------
compliant if {
    input.scc_enabled == true
    input.detection_scope_defined == true
    input.weekly_review_schedule_defined == true
    weekly_review_verified
    findings_available
    triage_verified
    remediation_verified
}

# ---------------------------
# SCC Findings Validation
# ---------------------------
findings_available if {
    count(get_array(input, "recent_findings")) > 0
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
    every ticket in input.triage_tickets {
        ticket.id != ""
        ticket.status != ""
        ticket.assignee != ""
        ticket.created_timestamp != ""
    }
}

# ---------------------------
# Remediation Validation
# ---------------------------
remediation_verified if {
    count(get_array(input, "remediation_actions")) > 0

    every action in input.remediation_actions {
        action.asset_id != ""
        action.action_type != ""
        action.timestamp != ""
        action.status == "COMPLETED"
    }
}

# ---------------------------
# Result
# ---------------------------
result := output if {

    findings := get_array(input, "recent_findings")
    tickets := get_array(input, "triage_tickets")
    actions := get_array(input, "remediation_actions")

    output := {
        "compliant": compliant,
        "message": generate_message,
        "affected_resources": findings,
        "details": {
            "scc_enabled": input.scc_enabled,
            "detection_scope": input.detection_scope,
            "weekly_review_frequency_days": input.review_frequency_days,
            "last_review_timestamp": input.last_review_timestamp,
            "scheduler_last_run_status": input.scheduler_last_run_status,
            "finding_count": count(findings),
            "ticket_count": count(tickets),
            "remediation_count": count(actions),
            "beyondcorp_enabled": input.beyondcorp_enabled,
            "context_aware_access_enabled": input.context_aware_access_enabled,
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
    not input.detection_scope_defined
    msg := "FAIL: SCC/CAI detection scope is not defined"
}

generate_message := msg if {
    input.detection_scope_defined
    not input.weekly_review_schedule_defined
    msg := "FAIL: No evidence of a scheduled weekly review process"
}

generate_message := msg if {
    input.weekly_review_schedule_defined
    not weekly_review_verified
    msg := "FAIL: Weekly review schedule exists but execution evidence is missing or unsuccessful"
}

generate_message := msg if {
    weekly_review_verified
    not findings_available
    msg := "INCONCLUSIVE: Weekly review verified but no SCC findings were provided as evidence"
}

generate_message := msg if {
    findings_available
    not triage_verified
    msg := "FAIL: Findings are not tracked through a documented triage workflow"
}

generate_message := msg if {
    triage_verified
    not remediation_verified
    msg := "FAIL: No evidence that unauthorized assets were remediated"
}

generate_message := msg if {
    compliant
    msg := "PASS: Unauthorized assets are identified weekly, triaged, and remediated using SCC/CAI with supporting evidence"
}

# ---------------------------
# Helper Function
# ---------------------------
get_array(obj, key) := value if {
    value := obj[key]
} else := []