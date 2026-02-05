# METADATA
# title: Ensure password expiration policy is set to never expire
# description: |
#   Configure password policies to never expire. NIST and Microsoft recommend
#   this approach when MFA is enabled, as forced password rotation leads to
#   weaker passwords without providing security benefits.
# related_resources:
# - ref: https://www.cisecurity.org/benchmark/microsoft_365
#   description: CIS Microsoft 365 Foundations Benchmark
# custom:
#   control_id: CIS-1.3.1
#   framework: cis
#   benchmark: microsoft-365-foundations
#   version: v4.0.0
#   severity: medium
#   service: EntraID
#   requires_permissions:
#   - Domain.Read.All

package cis.microsoft_365_foundations.v4_0_0.control_1_3_1

default result := {"compliant": false, "message": "Evaluation failed"}

# 2147483647 = "never expires" (max int32)
never_expires := 2147483647

result := output if {
    managed_domains := [d | some d in input.domains; d.is_managed == true]
    non_compliant := [d | some d in managed_domains; d.password_validity_days != never_expires]

    output := {
        "compliant": count(non_compliant) == 0,
        "message": generate_message(managed_domains, non_compliant),
        "affected_resources": [d.domain_name | some d in non_compliant],
        "details": {
            "total_managed_domains": count(managed_domains),
            "compliant_domains": count(managed_domains) - count(non_compliant),
            "non_compliant_domains": count(non_compliant),
            "domains": [{"name": d.domain_name, "password_validity_days": d.password_validity_days} | some d in managed_domains]
        }
    }
}

generate_message(managed_domains, non_compliant) := msg if {
    count(non_compliant) == 0
    msg := sprintf("All %d managed domain(s) have password expiration disabled", [count(managed_domains)])
}

generate_message(managed_domains, non_compliant) := msg if {
    count(non_compliant) > 0
    msg := sprintf("%d of %d managed domain(s) have password expiration enabled", [count(non_compliant), count(managed_domains)])
}
