package AutoAudit_tester.rules.CIS_GCP_2_12
import data.AutoAudit_tester.engine.Helpers as H

id           := "CIS_GCP_2_12"
title        := "Ensure That Cloud DNS Logging Is Enabled for All VPC Networks"
policy_group := "Logging and Monitoring"

remediation := `For each VPC network that needs a DNS policy with logging enabled:
gcloud dns policies create enable-dns-logging --enable-logging --
description="Enable DNS Logging" --networks=VPC_NETWORK_NAME
The VPC_NETWORK_NAME can be one or more networks in comma-separated list
Enable Logging for Existing DNS Policy
For each VPC network that has an existing DNS policy that needs logging enabled:
gcloud dns policies update POLICY_NAME --enable-logging --
networks=VPC_NETWORK_NAME
The VPC_NETWORK_NAME can be one or more networks in comma-separated list`

verification := `1. List all VPCs networks in a project:
gcloud compute networks list --format="table[box,title='All VPC
Networks'](name:label='VPC Network Name')"
2. List all DNS policies, logging enablement, and associated VPC networks:
gcloud dns policies list --flatten="networks[]" --
format="table[box,title='All DNS Policies By VPC Network'](name:label='Policy
Name',enableLogging:label='Logging
Enabled':align=center,networks.networkUrl.basename():label='VPC Network
Name')"
Each VPC Network should be associated with a DNS policy with logging enabled.`

# Any policy that attaches one or more networks must have enableLogging=true
deny := { v |
  some p
  p := input.dns.policies[_]
  count(p.networks) > 0
  not p.enableLogging
  v := sprintf("Project %q: Cloud DNS policy %q attaches VPCs but logging is disabled", [input.project_id, p.name])
}

report := H.build_report(deny, id, title, policy_group, verification, remediation)
