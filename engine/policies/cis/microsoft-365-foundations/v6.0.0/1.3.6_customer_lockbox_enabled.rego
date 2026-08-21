# METADATA
# title: Ensure the customer lockbox feature is enabled
# description: |
#   Customer Lockbox ensures that Microsoft cannot access customer 
#   content without explicit approval. When enabled, Microsoft must 
#   obtain customer approval before accessing data for support purposes.
# related_resources:
# - ref: https://learn.microsoft.com/en-us/purview/customer-lockbox-requests
#   description: Customer Lockbox overview
# custom:
#   control_id: CIS-1.3.6
#   framework: cis
#   benchmark: microsoft-365-foundations
#   version: v6.0.0
#   severity: high
#   service: Exchange
#   requires_permissions:
#   - Exchange.Manage

package cis.microsoft_365_foundations.v6_0_0.control_1_3_6

import rego.v1

default result := {
  "compliant": false,
  "message": "Unable to retrieve organization configuration",
  "details": {},
}

default compliant := false

# Compliant when Customer Lockbox is enabled
compliant if {
  input.organization_config.CustomerLockboxEnabled == true
}

msg := "Customer Lockbox is properly enabled" if {
  compliant
}

msg := "Customer Lockbox is disabled - Microsoft can access content without approval" if {
  not compliant
}
result := output if {
  lockbox_value := input.organization_config.CustomerLockboxEnabled

  output := {
    "compliant": compliant,
    "message": msg,
    "affected_resources": [],
    "details": {
      "customer_lockbox_enabled": lockbox_value,
    },
  }
}
