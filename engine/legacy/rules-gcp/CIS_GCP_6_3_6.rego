package AutoAudit_tester.rules.CIS_GCP_6_3_6
import data.AutoAudit_tester.engine.Helpers as H

id    := "CIS_GCP_6_3_6"
title := "SQL Server: '3625' trace flag = on"
policy_group := "Cloud SQL"
blocked_value := "on"

verification := `1. Ensure the below command returns on for every Cloud SQL SQL Server
database instance
gcloud sql instances describe <INSTANCE_NAME> --format=json | jq
'.settings.databaseFlags[] | select(.name=="3625")|.value'`

remediation := `1. Configure the 3625 database flag for every Cloud SQL SQL Server database
instance using the below command.
gcloud sql instances patch <INSTANCE_NAME> --database-flags "3625=on"`

deny := { v |  
  b := input[_]
  r := b.settings.databaseFlags[_]
  q := r.value
  s := r.name
  s == "3625"
  q != blocked_value
  v := sprintf("Ensure that log obscuration is enabled through trace flags and the attribute is set to a value: %q for a SQLserver Instances", [blocked_value])
}


report := H.build_report(deny, id, title, policy_group, verification, remediation)
