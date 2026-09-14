# METADATA
# title: Ensure 'Idle session timeout' is set to '3 hours (or less)' for unmanaged devices
# description: |
#   Idle session timeout signs users out of Microsoft 365 web apps after a period
#   of inactivity. Setting this to 3 hours or less reduces the risk of unauthorized
#   access from unattended or unmanaged devices.
# related_resources:
# - ref: https://www.cisecurity.org/benchmark/microsoft_365
#   description: CIS Microsoft 365 Foundations Benchmark
# custom:
#   control_id: CIS-1.3.2
#   framework: cis
#   benchmark: microsoft-365-foundations
#   version: v6.0.0
#   severity: medium
#   service: EntraID
#   requires_permissions:
#   - Policy.Read.All

package cis.microsoft_365_foundations.v6_0_0.control_1_3_2

import rego.v1

default result := {
  "compliant": false,
  "message": "Evaluation failed: unable to retrieve idle session timeout configuration",
  "details": {}
}

has_evidence := true if {
  input.idle_timeout_minutes != null
} else := false if { true }

collector_failed := true if {
  input.collector_error != null
  input.collector_error != ""
} else := false if { true }

compliant := true if {
  not collector_failed
  has_evidence
  input.idle_timeout_minutes > 0
  input.idle_timeout_minutes <= 180
} else := false if { true }

result := output if {
  timeout := input.idle_timeout_minutes
  unknown := not has_evidence
  failed := collector_failed

  output := {
    "compliant": compliant,
    "message": generate_message(compliant, unknown, failed),
    "affected_resources": generate_affected(compliant, unknown, failed),
    "details": {
      "idle_timeout_minutes": timeout,
      "idle_timeout_hours": timeout_hours(timeout),
      "total_policies": input.total_policies,
      "collector_error": input.collector_error
    }
  }
}

timeout_hours(minutes) := hours if {
  minutes != null
  hours := round(minutes / 60 * 100) / 100
} else := null if { true }

generate_message(true, false, false) := "Idle session timeout is set to 3 hours or less"
generate_message(false, false, false) := "Idle session timeout is not set, or exceeds 3 hours"
generate_message(_, true, false) := "Unable to determine the idle session timeout configuration"
generate_message(_, _, true) := "Collector failed to retrieve idle session timeout configuration"

generate_affected(true, false, false) := []
generate_affected(false, false, false) := ["Idle session timeout exceeds the maximum of 3 hours (180 minutes)"]
generate_affected(_, true, false) := ["Idle session timeout setting unknown"]
generate_affected(_, _, true) := ["Collector error prevented evaluation"]