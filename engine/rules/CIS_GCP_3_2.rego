package AutoAudit_tester.rules.CIS_GCP_3_2
import data.AutoAudit_tester.engine.Helpers as H

id    := "CIS_GCP_3_2"
title := "Ensure Legacy Networks Do Not Exist for Older Projects"
policy_group := "Networking"
blocked_value := "LEGACY"

verification := ` For each Google Cloud Platform project,
1. Set the project name in the Google Cloud Shell:
gcloud config set project <Project-ID>
2. List the networks configured in that project:
gcloud compute networks list
None of the listed networks should be in the legacy mode. `

remediation := ` For each Google Cloud Platform project,
1. Follow the documentation and create a non-legacy network suitable for the
organization's requirements.
2. Follow the documentation and delete the networks in the legacy mode. `

deny := { v |
  b := input[_]
  r := b.routingConfig.bgpBestPathSelectionMode
  r == blocked_value
  v := sprintf("Project network config should not contain %q Networks", [r])
}

report := H.build_report(deny, id, title, policy_group, verification, remediation)
