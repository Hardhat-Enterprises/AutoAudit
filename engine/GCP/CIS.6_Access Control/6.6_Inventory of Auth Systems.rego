# METADATA
# title: Ensure inventory of authentication and authorization systems is maintained (GCP)
# description: |
#   Organizations must maintain an up-to-date inventory of GCP authentication and authorization systems,
#   including Google Workspace / Cloud Identity, IAM configurations, and any federated identity providers.
#   Each system must have a defined owner and documented evidence of periodic (at least annual) review.
# related_resources:
# - ref: https://cloud.google.com/iam/docs
#   description: GCP IAM Documentation
# - ref: https://cloud.google.com/architecture/identity
#   description: Identity and Access Management in GCP
# custom:
#   control_id: CIS-6.6
#   framework: cis
#   benchmark: gcp-foundations
#   version: v2.0.0
#   severity: medium
#   service: IAM
#   requires_permissions:
#   - iam.securityReviewer

package cis.gcp_foundations.v2_0_0.control_6_6

import rego.v1

default compliant := false

# ---------------------------
# Compliance Logic
# ---------------------------
compliant if {
  count(input.inventory) > 0
  all_have_owner
  all_have_review_date
}

# Ensure every system has an assigned owner
all_have_owner if {
  not some i in input.inventory { i.owner == "" }
}

# Ensure every system has a recorded review date
all_have_review_date if {
  not some i in input.inventory { i.last_review == "" }
}

# ---------------------------
# Result Output
# ---------------------------
result := {
  "compliant": compliant,
  "message": generate_message,
  "details": {
    "inventory_size": count(input.inventory)
  }
}

# ---------------------------
# Message Logic
# ---------------------------
generate_message := "PASS: GCP authentication and authorization systems inventory is complete and maintained" if compliant

generate_message := "FAIL: Inventory missing ownership, review dates, or systems" if not compliant