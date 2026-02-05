# METADATA
# title: Ensure users installing Outlook add-ins is not allowed
# description: |
#   User installation of Outlook add-ins should be restricted to prevent
#   potentially malicious add-ins from accessing mailbox data. Add-in
#   installation should be centrally managed by administrators.
# related_resources:
# - ref: https://www.cisecurity.org/benchmark/microsoft_365
#   description: CIS Microsoft 365 Foundations Benchmark
# custom:
#   control_id: CIS-6.3.1
#   framework: cis
#   benchmark: microsoft-365-foundations
#   version: v6.0.0
#   severity: medium
#   service: Exchange
#   requires_permissions:
#   - Exchange.Manage

package cis.microsoft_365_foundations.v6_0_0.control_6_3_1

default result := {"compliant": false, "message": "Evaluation failed"}

result := output if {
    policies_allowing_addins := input.policies_allowing_addin_install

    # Compliant when no policies allow add-in installation
    compliant := count(policies_allowing_addins) == 0

    output := {
        "compliant": compliant,
        "message": generate_message(policies_allowing_addins),
        "affected_resources": [p.name | some p in policies_allowing_addins],
        "details": {
            "total_policies": input.total_policies,
            "policies_allowing_addins": count(policies_allowing_addins),
            "policy_details": policies_allowing_addins
        }
    }
}

generate_message(policies_allowing_addins) := msg if {
    count(policies_allowing_addins) == 0
    msg := "No role assignment policies allow user add-in installation"
}

generate_message(policies_allowing_addins) := msg if {
    count(policies_allowing_addins) > 0
    msg := sprintf("%d role assignment policy(ies) allow user add-in installation", [count(policies_allowing_addins)])
}
