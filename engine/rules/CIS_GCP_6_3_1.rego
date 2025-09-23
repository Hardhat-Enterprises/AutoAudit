package AutoAudit_tester.rules.CIS_GCP_6_3_1
import data.AutoAudit_tester.engine.Helpers as H

id    := "CIS_GCP_6_3_1"
title := "SQL Server: 'external scripts enabled' = off"
policy_group := "Cloud SQL"
blocked_value := "off"

verification := `1. Ensure the below command returns off for every Cloud SQL SQL Server
database instance
gcloud sql instances describe <INSTANCE_NAME> --format=json | jq
'.settings.databaseFlags[] | select(.name=="external scripts
enabled")|.value' 
In the output, database flags are listed under the settings as the collection
databaseFlags.`

remediation := `1. Configure the external scripts enabled database flag for every Cloud SQL
SQL Server database instance using the below command.
gcloud sql instances patch <INSTANCE_NAME> --database-flags "external scripts
enabled"=off`

deny := { v |  
  b := input[_]
  r := b.settings.databaseFlags[_]
  q := r.value
  s := r.name
  s == "external scripts enabled"
  q != blocked_value
  v := sprintf("Ensure that remote script execution is disabled and the external scripts enabled is set to the value: %q for a SQLserver Instances", [blocked_value])
}


report := H.build_report(deny, id, title, policy_group, verification, remediation)
