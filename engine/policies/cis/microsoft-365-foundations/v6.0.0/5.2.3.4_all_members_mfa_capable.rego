# METADATA
# title: Ensure all member users are 'MFA capable'
# description: Ensure all users have registered MFA methods.
# related_resources:
# - ref: https://learn.microsoft.com/en-us/graph/api/reportroot-list-authenticationmethods-userregistrationdetails
#   description: Authentication methods user registration details report
# custom:
#   control_id: CIS-5.2.3.4
#   framework: cis
#   benchmark: microsoft-365-foundations
#   version: v6.0.0
#   severity: high
#   service: EntraID
#   requires_permissions:
#   - AuditLog.Read.All

package cis.microsoft_365_foundations.v6_0_0.control_5_2_3_4

import rego.v1

default result := {
  "compliant": false,
  "message": "Unable to determine MFA capability across users",
  "details": {},
}

default compliant := false

compliant if {
  input.total_users > 0
  input.mfa_capable_count == input.total_users
}

msg := "All users are MFA capable" if { compliant }
msg := sprintf("%d of %d users are MFA capable", [input.mfa_capable_count, input.total_users]) if { not compliant }

result := output if {
  total := input.total_users
  capable := input.mfa_capable_count

  output := {
    "compliant": compliant,
    "message": msg,
    "details": {
      "total_users": total,
      "mfa_capable_count": capable,
      "mfa_registered_count": input.mfa_registered_count,
      "mfa_not_registered_count": input.mfa_not_registered_count,
      "mfa_registration_percentage": input.mfa_registration_percentage,
    },
  }
}

