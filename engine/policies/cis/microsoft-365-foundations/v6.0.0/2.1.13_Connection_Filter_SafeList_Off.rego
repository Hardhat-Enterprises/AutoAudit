# METADATA
# title: Ensure the connection filter safe list is off
# description: |
#   In Microsoft 365 organizations with Exchange Online mailboxes or standalone
#   Exchange Online Protection organizations without Exchange Online mailboxes
#   connection filtering and the default connection filter policy identify good or bad
#   source email servers by IP addresses. The key components of the default connection
#   filter policy are IP Allow List, IP Block List and Safe list.
#   The safe list is a pre-configured allow list that is dynamically updated by Microsoft.
#   The recommended safe list state is: Off or False
#  
# related_resources:
# - ref: https://www.cisecurity.org/benchmark/microsoft_365
#   description: CIS Microsoft 365 Foundations Benchmark
# custom:
#   control_id: CIS-2.1.13
#   framework: cis
#   benchmark: microsoft-365-foundations
#   version: v6.0.0
#   severity: medium
#   service: Exchange
#   requires_permissions:
#   - Exchange.Manage

package cis.microsoft_365_foundations.v6_0_0.control_2_1_13

import rego.v1

default result := {"compliant": false, "message": "Evaluation failed"}

enable_safe_list := object.get(input, "enable_safe_list", false)

result := {
    "compliant": true,
    "message": "EnableSafeList is False for Exchange Online Hosted Connection Filter",
    "affected_resources": [],
    "details": {"EnableSafeList": enable_safe_list}
} if enable_safe_list == false

result := {
    "compliant": false,
    "message": "EnableSafeList is not False for Exchange Online Hosted Connection Filter",
    "affected_resources": ["HostedConnectionFilterPolicy"],
    "details": {"EnableSafeList": enable_safe_list}
} if enable_safe_list == true
