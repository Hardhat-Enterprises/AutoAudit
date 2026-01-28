package AutoAudit_tester.rules.CIS_GCP_4_1
import data.AutoAudit_tester.engine.Helpers as H

id    := "CIS_GCP_4_1"
title := "Ensure That Instances Are Not Configured To Use the Default Service Account"
policy_group := "Compute"
blocked_value := "Company_Name"

verification := `1. List the instances in your project and get details on each instance:
gcloud compute instances list --format=json | jq -r . | "SA:
\(.[].serviceAccounts[].email) Name: \(.[].name)"
2. Ensure that the service account section has an email that does not match the
pattern [PROJECT_NUMBER]-compute@developer.gserviceaccount.com. `

remediation := `1. Stop the instance:
gcloud compute instances stop <INSTANCE_NAME>
2. Update the instance:
gcloud compute instances set-service-account <INSTANCE_NAME> --service-
account=<SERVICE_ACCOUNT>
3. Restart the instance:
gcloud compute instances start <INSTANCE_NAME`

deny := { v |
  b := input[_]
  r := b.serviceAccounts.email
  startswith(r, blocked_value)
  v := sprintf("Compute instance should not use default Compute engine service accounts like %q", [r])
}

report := H.build_report(deny, id, title, policy_group, verification, remediation)
