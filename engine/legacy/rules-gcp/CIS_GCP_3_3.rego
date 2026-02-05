package AutoAudit_tester.rules.CIS_GCP_3_3
import data.AutoAudit_tester.engine.Helpers as H
import future.keywords.in

id    := "CIS_GCP_3_3"
title := " Ensure That DNSSEC Is Enabled for Cloud DNS"
policy_group := "DNS Zones"
blocked_value := "on"

verification := ` 1. List all the Managed Zones in a project:
gcloud dns managed-zones list
2. For each zone of VISIBILITY public, get its metadata:
gcloud dns managed-zones describe ZONE_NAME
3. Ensure that dnssecConfig.state property is on. `

remediation := Use the below command to enable DNSSEC for Cloud DNS Zone Name.
gcloud dns managed-zones update ZONE_NAME --dnssec-state on `

deny := { v |  
  b := input[_]
  r := b.dnssecConfig.state
  r == blocked_value
  v := sprintf("Ensure that dnssecConfig is set to %q", [blocked_value])
}

report := H.build_report(deny, id, title, policy_group, verification, remediation)
