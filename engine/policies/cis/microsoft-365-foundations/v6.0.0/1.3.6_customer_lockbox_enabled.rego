package cis.microsoft_365_foundations.v6_0_0.control_1_3_6

import rego.v1

default result := {
    "compliant": false,
    "message": "Evaluation failed: unable to verify Customer Lockbox status",
    "details": {}
}

result := {
    "compliant": true,
    "message": "Customer Lockbox is enabled",
    "details": {"customer_lockbox_enabled": true}
} if {
    input.customer_lockbox_enabled == true
}

result := {
    "compliant": false,
    "message": "Customer Lockbox is not enabled",
    "details": {"customer_lockbox_enabled": false}
} if {
    input.customer_lockbox_enabled == false
}