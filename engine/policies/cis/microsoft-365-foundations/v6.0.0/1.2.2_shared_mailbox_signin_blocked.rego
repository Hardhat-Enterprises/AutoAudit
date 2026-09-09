# METADATA
# title: Ensure sign-in to shared mailboxes is blocked
# description: |
#   Shared mailboxes should not allow direct sign-in. Users should access them
#   through their own accounts using delegated permissions.
# related_resources:
# - ref: https://www.cisecurity.org/benchmark/microsoft_365
#   description: CIS Microsoft 365 Foundations Benchmark
# custom:
#   control_id: CIS-1.2.2
#   framework: cis
#   benchmark: microsoft-365-foundations
#   version: v6.0.0
#   severity: medium
#   service: Exchange
#   requires_permissions:
#   - Exchange.ManageAsApp

package cis.microsoft_365_foundations.v6_0_0.control_1_2_2

import rego.v1

default result := {
  "compliant": false,
  "message": "Evaluation failed: unable to verify shared mailbox sign-in status",
  "details": {}
}

default compliant := false

shared_mailboxes := object.get(input, "shared_mailboxes", [])

non_compliant_mailboxes := [
  mailbox |
  some mailbox in shared_mailboxes
  object.get(mailbox, "account_disabled", null) == false
]

unknown_status_mailboxes := [
  mailbox |
  some mailbox in shared_mailboxes
  object.get(mailbox, "account_disabled", null) == null
]

compliant if {
  count(unknown_status_mailboxes) == 0
  count(non_compliant_mailboxes) == 0
}

result := output if {
  count(unknown_status_mailboxes) == 0

  output := {
    "compliant": compliant,
    "message": generate_message(
      count(shared_mailboxes),
      count(non_compliant_mailboxes)
    ),
    "affected_resources": non_compliant_mailboxes,
    "details": {
      "total_shared_mailboxes": count(shared_mailboxes),
      "blocked_sign_in_count": count(shared_mailboxes) - count(non_compliant_mailboxes),
      "direct_sign_in_enabled_count": count(non_compliant_mailboxes)
    }
  }
}

result := output if {
  count(unknown_status_mailboxes) > 0

  output := {
    "compliant": false,
    "message": sprintf(
      "Unable to determine sign-in status for %d shared mailbox(es).",
      [count(unknown_status_mailboxes)]
    ),
    "affected_resources": unknown_status_mailboxes,
    "details": {
      "total_shared_mailboxes": count(shared_mailboxes),
      "unknown_status_count": count(unknown_status_mailboxes)
    }
  }
}

generate_message(total, non_compliant_count) := msg if {
  total == 0
  msg := "No shared mailboxes found."
}

generate_message(total, non_compliant_count) := msg if {
  total > 0
  non_compliant_count == 0
  msg := sprintf(
    "Sign-in is blocked for all %d shared mailbox(es).",
    [total]
  )
}

generate_message(total, non_compliant_count) := msg if {
  non_compliant_count > 0
  msg := sprintf(
    "%d of %d shared mailbox(es) allow direct sign-in.",
    [non_compliant_count, total]
  )
}