# METADATA
# title: Ensure users are restricted from recovering BitLocker keys
# description: Restrict BitLocker key recovery to admins.
# related_resources:
# - ref: https://www.cisecurity.org/benchmark/microsoft_365
#   description: CIS Microsoft 365 Foundations Benchmark
# custom:
#   control_id: CIS-5.1.4.6
#   framework: cis
#   benchmark: microsoft-365-foundations
#   version: v6.0.0
#   severity: medium
#   service: EntraID
#   requires_permissions:
#   - Policy.Read.All

package cis.microsoft_365_foundations.v6_0_0.control_5_1_4_6

import rego.v1

default result := {
  "compliant": false,
  "message": "Unable to determine allowedToReadBitlockerKeysForOwnedDevice",
  "details": {},
}

compliant_value := true if { input.allowed_to_read_bitlocker_keys_for_owned_device == false } else := false if { true }

msg := "Users are restricted from recovering BitLocker keys (allowedToReadBitlockerKeysForOwnedDevice=false)" if { input.allowed_to_read_bitlocker_keys_for_owned_device == false } else := "Users can recover BitLocker keys (allowedToReadBitlockerKeysForOwnedDevice=true)" if { input.allowed_to_read_bitlocker_keys_for_owned_device == true } else := "Unable to determine allowedToReadBitlockerKeysForOwnedDevice" if { true }

result := out if {
  value := input.allowed_to_read_bitlocker_keys_for_owned_device

  out := {
    "compliant": compliant_value,
    "message": msg,
    "details": {
      "allowed_to_read_bitlocker_keys_for_owned_device": value,
    },
  }
}

