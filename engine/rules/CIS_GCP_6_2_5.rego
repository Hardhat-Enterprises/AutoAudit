package AutoAudit_tester.rules.CIS_GCP_6_2_5
import data.AutoAudit_tester.engine.Helpers as H

id    := "CIS_GCP_6_2_5"
title := "PostgreSQL: 'log_min_messages' >= WARNING"
policy_group := "Cloud SQL"
blocked_value := ["WARNING", "ERROR", "LOG", "FATAL", "PANIC"]

verification := `1. Use the below command for every Cloud SQL PostgreSQL database instance to
verify that the value of log_min_messages is set to warning or higher .
gcloud sql instances describe [INSTANCE_NAME] --format=json | jq
'.settings.databaseFlags[] | select(.name=="log_min_messages")|.value'`

remediation := `1. Configure the log_min_messages database flag for every Cloud SQL
PosgreSQL database instance using the below command.
gcloud sql instances patch <INSTANCE_NAME> --database-flags
log_min_messages=<DEBUG5|DEBUG4|DEBUG3|DEBUG2|DEBUG1|INFO|NOTICE|WARNING|ERRO
R|LOG|FATAL|PANIC>`

deny := { v |  
  b := input[_]
  r := b.settings.databaseFlags[_]
  q := r.value
  s := r.name
  s == "log_min_messages"
  not q in blocked_value
  v := sprintf("Ensure that log_min_messages is set to a value above %q like: %q, %q, %q, %q or %q for PostgreSQL Instances", [r, blocked_value[0], blocked_value[1], blocked_value[2], blocked_value[3], blocked_value[4]])
}


report := H.build_report(deny, id, title, policy_group, verification, remediation)
