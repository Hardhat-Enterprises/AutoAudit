# METADATA
# title: Ensure additional storage providers are restricted in Outlook on the web
# description: |
#   Additional storage providers (Dropbox, Google Drive, Box, etc.) in Outlook
#   on the web can lead to data leakage if not properly controlled. Restrict
#   third-party storage providers to maintain data within corporate boundaries.
# related_resources:
# - ref: https://www.cisecurity.org/benchmark/microsoft_365
#   description: CIS Microsoft 365 Foundations Benchmark
# custom:
#   control_id: CIS-6.5.3
#   framework: cis
#   benchmark: microsoft-365-foundations
#   version: v6.0.0
#   severity: medium
#   service: Exchange
#   requires_permissions:
#   - Exchange.Manage

package cis.microsoft_365_foundations.v6_0_0.control_6_5_3

default result := {"compliant": false, "message": "Evaluation failed"}

result := output if {
    policies_with_external_storage := input.policies_with_external_storage
    total_policies := input.total_policies

    # Compliant when no policies allow external storage providers
    compliant := count(policies_with_external_storage) == 0

    output := {
        "compliant": compliant,
        "message": generate_message(policies_with_external_storage, total_policies),
        "affected_resources": policies_with_external_storage,
        "details": {
            "total_owa_policies": total_policies,
            "policies_with_external_storage": count(policies_with_external_storage),
            "policy_names": policies_with_external_storage
        }
    }
}

generate_message(policies_with_storage, total) := msg if {
    count(policies_with_storage) == 0
    msg := sprintf("All %d OWA mailbox policy(ies) restrict additional storage providers", [total])
}

generate_message(policies_with_storage, total) := msg if {
    count(policies_with_storage) > 0
    msg := sprintf("%d of %d OWA mailbox policy(ies) allow additional storage providers", [count(policies_with_storage), total])
}
