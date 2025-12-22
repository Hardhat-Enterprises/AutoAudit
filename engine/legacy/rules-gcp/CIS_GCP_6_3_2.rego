package AutoAudit_tester.rules.CIS_GCP_6_3_2
import data.AutoAudit_tester.engine.Helpers as H

id    := "CIS_GCP_6_3_2"
title := "SQL Server: 'cross db ownership chaining' = off"
policy_group := "Cloud SQL"
blocked_value := "off"

verification := `1. Ensure the below command returns off for every Cloud SQL SQL Server
database instance:
gcloud sql instances describe <INSTANCE_NAME> --format=json | jq
'.settings.databaseFlags[] | select(.name=="cross db ownership
chaining")|.value'
In the output, database flags are listed under the settings as the collection
databaseFlags.`

remediation := `1. Configure the cross db ownership chaining database flag for every Cloud
SQL SQL Server database instance using the below command:
gcloud sql instances patch <INSTANCE_NAME> --database-flags "cross db
ownership chaining"=off`

deny := { v |  
  b := input[_]
  r := b.settings.databaseFlags[_]
  q := r.value
  s := r.name
  s == "cross db ownership chaining"
  q != blocked_value
  v := sprintf("Ensure that cross db ownership chaining is disabled unless the entire database has it enabled and the attribute is set to the value: %q for a SQLserver Instances", [blocked_value])
}


report := H.build_report(deny, id, title, policy_group, verification, remediation)
