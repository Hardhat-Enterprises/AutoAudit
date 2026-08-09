package cis.microsoft_365_foundations.v6_0_0.control_1_3_7

import rego.v1

default result := {
    "compliant": false,
    "message": "Evaluation failed: unable to verify OWA mailbox policy settings",
    "details": {}
}

total_policies := object.get(input, "total_policies", 0)
policies_with_external_storage := object.get(input, "policies_with_external_storage", [])

default compliant := false

compliant if {
    total_policies > 0
    count(policies_with_external_storage) == 0
}

result := {
    "compliant": compliant,
    "message": message,
    "details": {
        "total_policies": total_policies,
        "policies_with_external_storage": policies_with_external_storage
    }
} if {
    total_policies > 0
}

message := "All OWA mailbox policies restrict third-party storage providers" if compliant
message := sprintf("%d OWA mailbox policy(ies) allow third-party storage providers: %v", [count(policies_with_external_storage), policies_with_external_storage]) if {
    not compliant
    total_policies > 0
}