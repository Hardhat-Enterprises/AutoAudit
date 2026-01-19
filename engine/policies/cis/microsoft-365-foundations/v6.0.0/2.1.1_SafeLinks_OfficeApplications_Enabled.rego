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

required_fields := {
    "ZapEnabled": true,
    "ExceptIfConditions": "valid_condition"
}

# Identify non-compliant fields in a policy
non_compliant_fields(p) := {f |
    # Manually check each required field
    f := "ZapEnabled"
    not p[f] = required_fields[f]
} 

non_compliant_fields(p) := {f |
    # Manually check each required field
    f := "ExceptIfConditions"
    not p[f] = required_fields[f]
}

# Check if a policy is compliant
policy_compliant(p) := true if count(non_compliant_fields(p)) == 0
policy_compliant(p) := false if count(non_compliant_fields(p)) > 0

# Generate a message based on compliance status
generate_message(true, _) := "All Teams Protection policies are configured according to CIS recommendations"
generate_message(false, non_compliant) := sprintf(
    "%d Teams Protection policy(ies) are not compliant with CIS recommendations",
    [count(non_compliant)]
)

# Generate list of affected resources
generate_affected_resources(true, _) := []
generate_affected_resources(false, non_compliant) := [
    {
        "identity": p.identity,
        "non_compliant_fields": [f | f := non_compliant_fields(p)[_]]
    } | p := non_compliant[_]
]

# Main evaluation
result := output if {
    policies := input.safe_links_policies

    # Identify non-compliant policies
    non_compliant := [p | p := policies[_]; not policy_compliant(p)]
    compliant := count(non_compliant) == 0

    output := {
        "compliant": compliant,
        "message": generate_message(compliant, non_compliant),
        "affected_resources": generate_affected_resources(compliant, non_compliant),
        "details": {
            "policies_checked": [p.identity | p := policies[_]],
            "required_fields": required_fields
        }
    }
}
