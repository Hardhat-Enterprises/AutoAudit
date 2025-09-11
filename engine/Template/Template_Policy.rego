package AutoAudit_tester.rules.CIS_GCP_POLICY_NUMBER
# Change this to match the actual policy number, e.g. CIS_GCP_1_5

import data.AutoAudit_tester.engine.Helpers as H

# -------------------------
# Policy Metadata (edit per control)
# -------------------------
id    := "CIS_GCP_POLICY_NUMBER"        # CIS Benchmark section, e.g. "CIS_GCP_1_5"
title := "POLICY DESCRIPTION"           # Human-readable name of the control
policy_group := "POLICY GROUP"          # e.g. "Identity and Access Management"

# -------------------------
# Parameters / constants
# -------------------------
# Example: Define values that should be blocked
blocked_roles := {"roles/owner", "roles/editor"}

# -------------------------
# Core logic
# -------------------------
# Build a set of violation messages. Each violation should return a descriptive string.
deny[v] {
  b := input.bindings[_]                  # Iterate through IAM bindings in the input
  r := b.role                             # Extract the role from the binding
  r in blocked_roles                      # Check if role is in the blocked set
  m := b.members[_]                       # Iterate through members of that role
  startswith(m, "serviceAccount:")        # Only check service accounts

  # Violation message (string, not object/set)
  v := sprintf("Service account %q must not have role %q", [m, r])
}

# -------------------------
# Standardized Report Output
# -------------------------
# This calls the shared helper to generate a clean report object:
# {
#   "id": "CIS_GCP_POLICY_NUMBER",
#   "title": "POLICY DESCRIPTION",
#   "input_kind": "POLICY GROUP",
#   "status": "NonCompliant/Compliant",
#   "counts": {"violations": <int>},
#   "violations": "<single text message or semicolon-separated list>"
# }
report := H.report(id, title, policy_group, deny)