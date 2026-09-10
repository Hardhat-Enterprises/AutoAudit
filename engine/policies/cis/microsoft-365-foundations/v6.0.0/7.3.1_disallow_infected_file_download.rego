# METADATA
# title: Ensure Office 365 SharePoint infected files are disallowed for download
# description: |
#   By default, SharePoint Online allows files that Defender for Office 365
#   has detected as infected to be downloaded. Disallowing download of
#   infected files prevents inadvertent sharing of malicious content.
# related_resources:
# - ref: https://www.cisecurity.org/benchmark/microsoft_365
#   description: CIS Microsoft 365 Foundations Benchmark
# custom:
#   control_id: CIS-7.3.1
#   framework: cis
#   benchmark: microsoft-365-foundations
#   version: v6.0.0
#   severity: high
#   service: SharePoint
#   requires_permissions:
#   - SharePoint.Admin

package cis.microsoft_365_foundations.v6_0_0.control_7_3_1

default result := {"compliant": false, "message": "Evaluation failed"}

result := output if {
    disallow_infected_file_download := input.disallow_infected_file_download

    # Compliant when DisallowInfectedFileDownload is true
    compliant := disallow_infected_file_download == true

    output := {
        "compliant": compliant,
        "message": generate_message(disallow_infected_file_download),
        "affected_resources": generate_affected_resources(compliant),
        "details": {
            "disallow_infected_file_download": disallow_infected_file_download
        }
    }
}

generate_message(disallow_infected_file_download) := msg if {
    disallow_infected_file_download == true
    msg := "Infected SharePoint files are disallowed for download"
}

generate_message(disallow_infected_file_download) := msg if {
    disallow_infected_file_download == false
    msg := "Infected SharePoint files are allowed for download (DisallowInfectedFileDownload is False)"
}

generate_message(disallow_infected_file_download) := msg if {
    disallow_infected_file_download == null
    msg := "Unable to determine DisallowInfectedFileDownload status"
}

generate_affected_resources(true) := []
generate_affected_resources(false) := ["Infected SharePoint files can be downloaded"]
