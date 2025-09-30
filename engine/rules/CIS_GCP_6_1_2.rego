package AutoAudit_tester.rules.CIS_GCP_6_1_2
import data.AutoAudit_tester.engine.Helpers as H

id    := "CIS_GCP_6_1_2"
title := "MySQL: Ensure 'skip_show_database' flag is ON"
policy_group := "Cloud SQL"
blocked_value := "on"

verification := `1. List all Cloud SQL database Instances
gcloud sql instances list
2. Ensure the below command returns on for every Cloud SQL Mysql database
instance 
gcloud sql instances describe <INSTANCE_NAME> --format=json | jq
'.settings.databaseFlags[] | select(.name=="skip_show_database")|.value' `

remediation := `1. List all Cloud SQL database Instances
gcloud sql instances list
2. Configure the skip_show_database database flag for every Cloud SQL Mysql
database instance using the below command.
gcloud sql instances patch <INSTANCE_NAME> --database-flags
skip_show_database=on`

deny := { v |  
  b := input[_]
  r := b.settings.databaseFlags[_]
  q := r.value
  s := r.name
  s == "skip_show_database"
  q != blocked_value
  v := sprintf("Ensure that skip_show_database flasg is set to %q for MYSQL Instances", [blocked_value])
}


report := H.build_report(deny, id, title, policy_group, verification, remediation)
