# METADATA
# title: Ensure 'Access reviews' for Guest Users are configured
# description: Configure access reviews for guest users.
# related_resources:
# - ref: https://learn.microsoft.com/en-us/graph/api/resources/accessreviewset
#   description: Access reviews
# custom:
#   control_id: CIS-5.3.2
#   framework: cis
#   benchmark: microsoft-365-foundations
#   version: v6.0.0
#   severity: medium
#   service: EntraID
#   requires_permissions:
#   - AccessReview.Read.All

package cis.microsoft_365_foundations.v6_0_0.control_5_3_2

import rego.v1

default result := {
  "compliant": false,
  "message": "Unable to determine guest access reviews",
  "details": {},
}

default compliant := false

compliant if { input.has_guest_reviews == true }

msg := "Guest user access reviews are configured" if { compliant }
msg := "No guest user access reviews are configured" if { not compliant }

result := output if {
  has := input.has_guest_reviews

  output := {
    "compliant": compliant,
    "message": msg,
    "details": {
      "total_reviews": input.total_reviews,
      "guest_reviews_count": input.guest_reviews_count,
    },
  }
}

