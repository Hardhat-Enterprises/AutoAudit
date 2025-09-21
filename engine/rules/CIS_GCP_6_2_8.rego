package AutoAudit_tester.rules.CIS_GCP_6_2_8
import data.AutoAudit_tester.engine.Helpers as H

id    := "CIS_GCP_6_2_8"
title := "PostgreSQL: 'cloudsql.enable_pgaudit' = on"
policy_group := "Cloud SQL"
blocked_value := "on"

verification := `Run the command by providing <INSTANCE_NAME>. Ensure the value of the flag is on.
gcloud sql instances describe <INSTANCE_NAME> --format="json" | jq
'.settings|.|.databaseFlags[]|select(.name=="cloudsql.enable_pgaudit")|.value`

remediation := `Run the below command by providing <INSTANCE_NAME> to enable
cloudsql.enable_pgaudit flag.
gcloud sql instances patch <INSTANCE_NAME> --database-flags
cloudsql.enable_pgaudit=on
Note: RESTART is required to get this configuration in effect.`

deny := { v |  
  b := input[_]
  r := b.settings.databaseFlags[_]
  q := r.value
  s := r.name
  s == "cloudsql.enable_pgaudit"
  q != blocked_value
  v := sprintf("Ensure that pgaudit is enabled for centralised logging and the cloudsql.pgaudit is set to the value: %q for PostgreSQL Instances", [blocked_value])
}


report := H.build_report(deny, id, title, policy_group, verification, remediation)
