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

default result := {"compliant": false, "message": "Evaluation failed"}

safe_links_policies := object.get(input, "safe_links_policies", [])

office_enabled_policies := [p |
    p := safe_links_policies[_]
    p.EnableSafeLinksForOffice == true
]

non_compliant_policies := [p |
    p := safe_links_policies[_]
    p.EnableSafeLinksForOffice != true
]

policy_name(p) := name if {
    name := object.get(p, "Name", null)
    name != null
} else := identity if {
    identity := object.get(p, "Identity", null)
    identity != null
} else := "Unknown policy"

generate_message(true, _) := "Safe Links for Office applications is enabled in at least one policy."
generate_message(false, false) := "No Safe Links policies were found to evaluate."
generate_message(false, true) := "Safe Links for Office applications is not enabled in any policy."

generate_affected_resources(true, _, _) := []
generate_affected_resources(false, false, _) := ["SafeLinksPolicy"]
generate_affected_resources(false, true, non_compliant) := [policy_name(p) | p := non_compliant[_]]

result := output if {
    has_policies := count(safe_links_policies) > 0
    compliant := count(office_enabled_policies) > 0

    output := {
        "compliant": compliant,
        "message": generate_message(compliant, has_policies),
        "affected_resources": generate_affected_resources(compliant, has_policies, non_compliant_policies),
        "details": {
            "total_policies": count(safe_links_policies),
            "office_enabled_count": count(office_enabled_policies),
            "office_enabled_policies": [policy_name(p) | p := office_enabled_policies[_]]
        }
    }
}
