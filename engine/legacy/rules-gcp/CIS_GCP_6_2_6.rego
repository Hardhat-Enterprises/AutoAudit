package AutoAudit_tester.rules.CIS_GCP_6_2_6
import data.AutoAudit_tester.engine.Helpers as H

id    := "CIS_GCP_6_2_6"
title := "PostgreSQL: 'log_min_error_statement' >= ERROR"
policy_group := "Cloud SQL"
blocked_value := ["ERROR", "LOG", "FATAL", "PANIC"]

verification := `1. Use the below command for every Cloud SQL PostgreSQL database instance to
verify the value of log_min_error_statement is set to ERROR or stricter.
gcloud sql instances describe <INSTANCE_NAME> --format=json | jq
'.[].settings.databaseFlags[] |
select(.name=="log_min_error_statement")|.value'
In the output, database flags are listed under the settings as the collection
databaseFlags.`

remediation := `from Google Cloud CLI
1. Configure the log_min_error_statement database flag for every Cloud SQL
PosgreSQL database instance using the below command.
gcloud sql instances patch <INSTANCE_NAME> --database-flags
log_min_error_statement=<DEBUG5|DEBUG4|DEBUG3|DEBUG2|DEBUG1|INFO|NOTICE|WARNI
NG|ERROR>`

deny := { v |  
  b := input[_]
  r := b.settings.databaseFlags[_]
  q := r.value
  s := r.name
  s == "log_min_messages"
  not q in blocked_value
  v := sprintf("Ensure that log_min_error_statement is set to a value above %q like: %q, %q, %q or %q for PostgreSQL Instances", [r, blocked_value[0], blocked_value[1], blocked_value[2], blocked_value[3]])
}


report := H.build_report(deny, id, title, policy_group, verification, remediation)
