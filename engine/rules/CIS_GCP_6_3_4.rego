package AutoAudit_tester.rules.CIS_GCP_6_3_4
import data.AutoAudit_tester.engine.Helpers as H

id    := "CIS_GCP_6_3_4"
title := "SQL Server: 'user options' not configured"
policy_group := "Cloud SQL"
blocked_value := ""

verification := `1. Ensure the below command returns empty result for every Cloud SQL SQL
Server database instance
gcloud sql instances describe <INSTANCE_NAME> --format=json | jq
'.settings.databaseFlags[] | select(.name=="user options")|.value'
In the output, database flags are listed under the settings as the collection
databaseFlags.`

remediation := `1. List all Cloud SQL database Instances
gcloud sql instances list
2. Clear the user options database flag for every Cloud SQL SQL Server
database instance using either of the below commands.
Clearing all flags to their default value
gcloud sql instances patch <INSTANCE_NAME> --clear-database-flags`

deny := { v |  
  b := input[_]
  r := b.settings.databaseFlags[_]
  q := r.value
  s := r.name
  s == "user options"
  q != blocked_value
  v := sprintf("Ensure that user options flag is not configured because it can be overidden with SET command and the attribute is set to a null string value: %q for a SQLserver Instances", [blocked_value])
}


report := H.build_report(deny, id, title, policy_group, verification, remediation)
