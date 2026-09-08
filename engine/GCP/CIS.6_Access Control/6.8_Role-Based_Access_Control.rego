# METADATA
# title: Ensure role-based access control is defined and maintained (GCP)
# description: |
#   Access to GCP resources must be assigned using IAM roles mapped to job functions.
#   Access should be granted via Google Groups where possible instead of direct user bindings,
#   and role assignments must be reviewed regularly with documented evidence.
# related_resources:
# - ref: https://cloud.google.com/iam/docs/understanding-roles
#   description: GCP IAM Roles Overview
# - ref: https://cloud.google.com/iam/docs/groups
#   description: Google Groups and IAM
# custom:
#   control_id: CIS-6.8
#   framework: cis
#   benchmark: gcp-foundations
#   version: v2.0.0
#   severity: high
#   service: IAM
#   requires_permissions:
#   - iam.securityReviewer

package cis.gcp_foundations.v2_0_0.control_6_8

import rego.v1

default compliant := false

# ---------------------------
# Compliance Logic
# ---------------------------
compliant if {
  count(input.roles) > 0                   # IAM roles defined
  input.group_based_assignment == true     # Access via Google Groups
  has_review_record
}

# Validate at least one access review record exists
has_review_record if {
  some r in input.access_reviews

  r.review_date != ""
  r.reviewer != ""
}

# ---------------------------
# Result Output
# ---------------------------
result := {
  "compliant": compliant,
  "message": generate_message,
  "details": {
    "role_count": count(input.roles),
    "review_count": count(input.access_reviews)
  }
}

# ---------------------------
# Message Logic
# ---------------------------
generate_message := "PASS: GCP IAM role-based access control is defined, enforced via groups, and regularly reviewed" if compliant

generate_message := "FAIL: RBAC in GCP is not properly defined, enforced, or reviewed" if not compliant