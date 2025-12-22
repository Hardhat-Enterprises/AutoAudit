package AutoAudit_tester.rules.CIS_GCP_3_1
import data.AutoAudit_tester.engine.Helpers as H

id    := "CIS_GCP_3_1"
title := "Ensure That the Default Network Does Not Exist in a Project"
policy_group := "Networking"
blocked_value := "default"

verification := ` 1. Set the project name in the Google Cloud Shell:
gcloud config set project PROJECT_ID
2. List the networks configured in that project:
gcloud compute networks list
It should not list default as one of the available networks in that project. `

remediation := 1. Set the project name in the Google Cloud Shell:
gcloud config set project PROJECT_ID
2. List the networks configured in that project:
gcloud compute networks list
It should not list default as one of the available networks in that project. `

deny := { v |
  b := input[_]
  r := b.name
  r == blocked_value
  v := sprintf("project should not have network name: %q", [r])
}

report := H.build_report(deny, id, title, policy_group, verification, remediation)
