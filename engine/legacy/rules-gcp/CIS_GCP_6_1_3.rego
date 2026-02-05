package AutoAudit_tester.rules.CIS_GCP_6_1_3
import data.AutoAudit_tester.engine.Helpers as H

id    := "CIS_GCP_6_1_3"
title := "MySQL: Ensure 'local_infile' flag is OFF"
policy_group := "Cloud SQL"
blocked_value := "off"

verification := `1. List all Cloud SQL database instances:
gcloud sql instances list
2. Ensure the below command returns off for every Cloud SQL MySQL database
instance.
gcloud sql instances describe <INSTANCE_NAME> --format=json | jq
'.settings.databaseFlags[] | select(.name=="local_infile")|.value' `

remediation := `1. List all Cloud SQL database instances using the following command:
gcloud sql instances list
2. Configure the local_infile database flag for every Cloud SQL Mysql database
instance using the below command:
gcloud sql instances patch <INSTANCE_NAME> --database-flags local_infile=off`

deny := { v |  
  b := input[_]
  r := b.settings.databaseFlags[_]
  q := r.value
  s := r.name
  s == "local_infile"
  q != blocked_value
  v := sprintf("Ensure that local_infile flag is set to %q for MYSQL Instances", [blocked_value])
}


report := H.build_report(deny, id, title, policy_group, verification, remediation)
