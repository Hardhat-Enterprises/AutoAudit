# METADATA
# title: Ensure DMARC Records for all Exchange Online domains are published
# description: |
#   DMARC, or Domain-based Message Authentication, Reporting, and Conformance, 
#   assists recipient mail systems in determining the appropriate action to take when 
#   messages from a domain fail to meet SPF or DKIM authentication criteria.
#   Ensure that the record exists that has the following flags defined either
#   p=quarantine OR p=reject.
# related_resources:
# - ref: https://www.cisecurity.org/benchmark/microsoft_365
#   description: CIS Microsoft 365 Foundations Benchmark
# custom:
#   control_id: CIS-2.1.10
#   framework: cis
#   benchmark: microsoft-365-foundations
#   version: v6.0.0
#   severity: high
#   service: Exchange
#   requires_permissions:
#   - Exchange.Manage

package cis.microsoft_365_foundations.v6_0_0.control_2_1_10

default result := {"compliant": false, "message": "Evaluation failed"}

result := output if {
    domains := input.domains

    # Collect all domains where DMARC records are missing or empty
    dmarc_issues := [d | d := domains[_]; not dmarc_record_published(d)]

    compliant := count(dmarc_issues) == 0

    output := {
        "compliant": compliant,
        "message": generate_message(compliant, dmarc_issues),
        "affected_resources": generate_affected_resources(compliant, dmarc_issues),
        "details": {
            "total_domains": count(domains),
            "non_compliant_domains_count": count(dmarc_issues),
            "non_compliant_domains": dmarc_issues
        }
    }
}

dmarc_record_published(domain) if {
    domain.dmarc_record
    dmarc := lower(domain.dmarc_record)
    dmarc != ""
    startswith(dmarc, "v=dmarc1")

    tags := [trim_space(t) | t := split(dmarc, ";")[_]]
    some i
    tag := tags[i]
    startswith(tag, "p=")
    policy := trim_space(substring(tag, 2, count(tag)-2))
    policy in {"quarantine", "reject"}
}

generate_message(true, _) := "All Exchange domains have DMARC records published."
generate_message(false, dmarc_issues) := sprintf(
    "%d domain(s) are missing DMARC records",
    [count(dmarc_issues)]
)

generate_affected_resources(true, _) := []
generate_affected_resources(false, dmarc_issues) := [d.domain | d := dmarc_issues[_]]
