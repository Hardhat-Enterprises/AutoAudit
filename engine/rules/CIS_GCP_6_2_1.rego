package AutoAudit_tester.rules.CIS_GCP_6_2_1
import data.AutoAudit_tester.engine.Helpers as H

id    := "CIS_GCP_6_2_1"
title := "PostgreSQL: 'log_error_verbosity' DEFAULT or stricter"
policy_group := "Cloud SQL"
blocked_value := ["TERSE", "DEFAULT"]

verification := `1. Use the below command for every Cloud SQL PostgreSQL database instance to
verify the value of log_error_verbosity
gcloud sql instances describe [INSTANCE_NAME] --format=json | jq
'.settings.databaseFlags[] | select(.name=="log_error_verbosity")|.value'
In the output, database flags are listed under the settings as the collection
databaseFlags.`

remediation := `1. Configure the log_error_verbosity database flag for every Cloud SQL PosgreSQL
database instance using the below command.
gcloud sql instances patch INSTANCE_NAME --database-flags
log_error_verbosity=<TERSE|DEFAULT|VERBOSE>`

deny := { v |  
  b := input[_]
  r := b.settings.databaseFlags[_]
  q := r.value
  s := r.name
  s == "log_error_verbosity"
  not q in blocked_value
  v := sprintf("Ensure that log_error_verbosity is set to either %q or %q for PostgreSQL Instances", [blocked_value[0], blocked_value[1]])
}


report := H.build_report(deny, id, title, policy_group, verification, remediation)
