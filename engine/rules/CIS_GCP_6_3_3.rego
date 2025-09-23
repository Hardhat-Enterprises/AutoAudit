package AutoAudit_tester.rules.CIS_GCP_6_3_3
import data.AutoAudit_tester.engine.Helpers as H

id    := "CIS_GCP_6_3_3"
title := "SQL Server: 'user connections' = 0 (non-limiting)"
policy_group := "Cloud SQL"
blocked_value := "0"

verification := `1. Ensure the below command returns a value of 0, for every Cloud SQL SQL
Server database instance.
gcloud sql instances describe <INSTANCE_NAME> --format=json | jq
'.settings.databaseFlags[] | select(.name=="user connections")|.value'`

remediation := `1. Configure the user connections database flag for every Cloud SQL SQL
Server database instance using the below command.
gcloud sql instances patch <INSTANCE_NAME> --database-flags "user
connections=[0-32,767]"`

deny := { v |  
  b := input[_]
  r := b.settings.databaseFlags[_]
  q := r.value
  s := r.name
  s == "user connections"
  q != blocked_value
  v := sprintf("Ensure that simulataneous user connections value is set to default so it utilises the SQL server capabilities to impose the limit and the attribute is set to the value: %q for a SQLserver Instances", [blocked_value])
}


report := H.build_report(deny, id, title, policy_group, verification, remediation)
