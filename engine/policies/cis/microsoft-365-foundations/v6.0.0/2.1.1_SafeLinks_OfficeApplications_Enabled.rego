# METADATA
# title: Ensure Safe Links for Office Applications is Enabled
# description: |
#   Enabling Safe Links policy for Office applications allows URL's that exist 
#   inside of Office documents and email applications opened by Office, Office Online
#   and Office mobile to be processed against Defender.
#  
# related_resources:
# - ref: https://www.cisecurity.org/benchmark/microsoft_365
#   description: CIS Microsoft 365 Foundations Benchmark
# custom:
#   control_id: CIS-2.1.1
#   framework: cis
#   benchmark: microsoft-365-foundations
#   version: v6.0.0
#   severity: high
#   service: Exchange
#   requires_permissions:
#   - Exchange.Manage

package cis.microsoft_365_foundations.v6_0_0.control_2_1_1

import rego.v1

default result := {"compliant": false, "message": "Evaluation failed"}

required_fields := {
    "EnableSafeLinksForEmail": true,
    "EnableSafeLinksForTeams": true,
    "EnableSafeLinksForOffice": true,
    "TrackClicks": true,
    "AllowClickThrough": false,
    "ScanUrls": true,
    "EnableForInternalSenders": true,
    "DeliverMessageAfterScan": true,
    "DisableUrlRewrite": false
}

missing_sentinel := "__missing__"

field_non_compliant(p, f) if {
    object.get(p, f, missing_sentinel) == missing_sentinel
}

field_non_compliant(p, f) if {
    object.get(p, f, missing_sentinel) != missing_sentinel
    p[f] != required_fields[f]
}

non_compliant_fields(p) := fields if {
    fields := {f |
        some f
        required_fields[f]      # f is a key in required_fields
        field_non_compliant(p, f)
    }
}

policy_compliant(p) := true if {
    count(non_compliant_fields(p)) == 0
}

policy_compliant(p) := false if {
    count(non_compliant_fields(p)) > 0
}

generate_message(true, _) := "All Safe Links policies for Office applications are compliant"
generate_message_no_policies := "No Safe Links policies found for Office applications"

generate_message(false, non_compliant) := sprintf(
    "%d Safe Links policy(ies) for Office applications are not compliant",
    [count(non_compliant)]
)

generate_affected_resources(true, _) := []

generate_affected_resources(false, non_compliant) := resources if {
    resources := [
        {
            "identity": object.get(p, "Identity", object.get(p, "Name", null)),
            "non_compliant_fields": [f | f := non_compliant_fields(p)[_]]
        } |
        p := non_compliant[_]
    ]
}

no_policies_result := {
    "compliant": false,
    "message": generate_message_no_policies,
    "affected_resources": [{"identity": "Safe Links policy", "non_compliant_fields": ["missing_policy"]}],
    "details": {
        "policies_checked": [],
        "required_fields": required_fields
    }
}

with_policies_result(policies, non_compliant) := {
    "compliant": count(non_compliant) == 0,
    "message": generate_message(count(non_compliant) == 0, non_compliant),
    "affected_resources": generate_affected_resources(count(non_compliant) == 0, non_compliant),
    "details": {
        "policies_checked": [object.get(p, "Identity", object.get(p, "Name", null)) | p := policies[_]],
        "required_fields": required_fields
    }
}

result := output if {
    policies := object.get(input, "safe_links_policies", [])
    count(policies) == 0
    output := no_policies_result
}

result := output if {
    policies := object.get(input, "safe_links_policies", [])
    count(policies) > 0

    non_compliant := [
        p |
        p := policies[_]
        not policy_compliant(p)
    ]

    output := with_policies_result(policies, non_compliant)
}
