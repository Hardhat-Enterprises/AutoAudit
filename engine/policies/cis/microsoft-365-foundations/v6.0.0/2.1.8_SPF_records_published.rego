# METADATA
# title: Ensure that SPF records are published for all Exchange Domains
# description: |
#   A corresponding Sender Policy Framework (SPF) record
#   should be created for each domain that will be configured in Exchange.
#  
# related_resources:
# - ref: https://www.cisecurity.org/benchmark/microsoft_365
#   description: CIS Microsoft 365 Foundations Benchmark
# custom:
#   control_id: CIS-2.1.8
#   framework: cis
#   benchmark: microsoft-365-foundations
#   version: v6.0.0
#   severity: high
#   service: Exchange
#   requires_permissions:
#   - Exchange.Manage

package cis.microsoft_365_foundations.v6_0_0.control_2_1_8

default result := {"compliant": false, "message": "Evaluation failed"}

result := output if {
    domains := input.domains

    # Collect all domains where SPF records are missing or empty
    spf_issues := [d | d := domains[_]; not spf_record_published(d)]

    compliant := count(spf_issues) == 0

    output := {
        "compliant": compliant,
        "message": generate_message(compliant, spf_issues),
        "affected_resources": generate_affected_resources(compliant, spf_issues),
        "details": {
            "total_domains": count(domains),
            "non_compliant_domains_count": count(spf_issues),
            "non_compliant_domains": spf_issues
        }
    }
}

spf_record_published(domain) if {
    record := trim(domain.spf_record, " \t\r\n")
    record != ""
    startswith(lower(record), "v=spf1")
}

generate_message(true, _) := "All Exchange domains have SPF records published."

generate_message(false, spf_issues) := sprintf(
    "%d domain(s) do not have a valid SPF record (v=spf1...) published",
    [count(spf_issues)]
)

generate_affected_resources(true, _) := []
generate_affected_resources(false, spf_issues) := [d.domain | d := spf_issues[_]]