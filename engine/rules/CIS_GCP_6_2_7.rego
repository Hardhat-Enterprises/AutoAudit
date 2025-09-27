package AutoAudit_tester.rules.CIS_GCP_6_2_7
import data.AutoAudit_tester.engine.Helpers as H

id    := "CIS_GCP_6_2_7"
title := "PostgreSQL: 'log_min_duration_statement' = -1 (disabled)"
policy_group := "Cloud SQL"
blocked_value := "-1"

verification := `1. Use the below command for every Cloud SQL PostgreSQL database instance to
verify the value of log_min_duration_statement is set to -1.
gcloud sql instances describe <INSTANCE_NAME> --format=json| jq
'.settings.databaseFlags[] |
select(.name=="log_min_duration_statement")|.value'
In the output, database flags are listed under the settings as the collection
databaseFlags.`

remediation := `1. List all Cloud SQL database instances using the following command:
gcloud sql instances list
2. Configure the log_min_duration_statement flag for every Cloud SQL
PosgreSQL database instance using the below command:
gcloud sql instances patch <INSTANCE_NAME> --database-flags
log_min_duration_statement=-1`

deny := { v |  
  b := input[_]
  r := b.settings.databaseFlags[_]
  q := r.value
  s := r.name
  s == "log_min_duration_statement"
  q != blocked_value
  v := sprintf("Ensure that log_min_duration_statement is disabled and set to the value: %q for PostgreSQL Instances", [blocked_value])
}


report := H.build_report(deny, id, title, policy_group, verification, remediation)
