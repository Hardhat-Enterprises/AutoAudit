package AutoAudit_tester.rules.CIS_GCP_6_7
import data.AutoAudit_tester.engine.Helpers as H

id    := "CIS_GCP_6_7"
title := "Ensure Cloud SQL automated backups are enabled"
policy_group := "Cloud SQL"
blocked_value := "True"

verification := `1. List all Cloud SQL database instances using the following command:
gcloud sql instances list --format=json | jq '. | map(select(.instanceType !=
"READ_REPLICA_INSTANCE")) | .[].name'
2. Ensure that the below command returns True for every Cloud SQL database
instance.
gcloud sql instances describe <INSTANCE_NAME> --
format="value('Enabled':settings.backupConfiguration.enabled)"`

remediation := `1. List all Cloud SQL database instances using the following command:
gcloud sql instances list --format=json | jq '. | map(select(.instanceType !=
"READ_REPLICA_INSTANCE")) | .[].name'
2. Enable Automated backups for every Cloud SQL database instance using the
below command:
gcloud sql instances patch <INSTANCE_NAME> --backup-start-time <[HH:MM]>
The backup-start-time parameter is specified in 24-hour time, in the UTC±00 time
zone, and specifies the start of a 4-hour backup window. Backups can start any time
during the backup window.`

deny := { v |  
  b := input[_]
  r := b.settings.backupConfiguration.enabled
  r != blocked_value
  v := sprintf("Ensure that automated backups are always turned on for any SQL server and that the attribute is always set to a value: %q for a SQLserver Instances", [blocked_value])
}


report := H.build_report(deny, id, title, policy_group, verification, remediation)
