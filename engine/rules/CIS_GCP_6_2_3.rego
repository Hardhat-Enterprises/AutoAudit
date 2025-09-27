package AutoAudit_tester.rules.CIS_GCP_6_2_3
import data.AutoAudit_tester.engine.Helpers as H

id    := "CIS_GCP_6_2_3"
title := "PostgreSQL: 'log_disconnections' = on"
policy_group := "Cloud SQL"
blocked_value := "on"

verification := `1. Ensure the below command returns on for every Cloud SQL PostgreSQL
database instance:
gcloud sql instances list --format=json | jq '.[].settings.databaseFlags[] |
select(.name=="log_disconnections")|.value`

remediation := `1. Configure the log_disconnections database flag for every Cloud SQL
PosgreSQL database instance using the below command:
gcloud sql instances patch <INSTANCE_NAME> --database-flags
log_disconnections=on`

deny := { v |  
  b := input[_]
  r := b.settings.databaseFlags[_]
  q := r.value
  s := r.name
  s == "log_disconnections"
  q != blocked_value
  v := sprintf("Ensure that log_disconnections is set to either %q for PostgreSQL Instances", [blocked_value])
}


report := H.build_report(deny, id, title, policy_group, verification, remediation)
