package AutoAudit_tester.rules.CIS_GCP_8_1
import data.AutoAudit_tester.engine.Helpers as H

id    := "CIS_GCP_8_1"
title := "Ensure Dataproc clusters are encrypted using CMEK"
policy_group := "Dataproc"
blocked_value := ""

verification := `List the name of all datasets.
bq ls
Retrieve each dataset details using the following command:
bq show PROJECT_ID:DATASET_NAME
Ensure that allUsers and allAuthenticatedUsers have not been granted access to
the dataset.`

remediation := `List the name of all datasets.
bq ls
Retrieve the data set details:
bq show --format=prettyjson PROJECT_ID:DATASET_NAME > PATH_TO_FILE
In the access section of the JSON file, update the dataset information to remove all
roles containing allUsers or allAuthenticatedUsers.
Update the dataset:
bq update --source PATH_TO_FILE PROJECT_ID:DATASET_NAME`

deny := { v |  
  b := input[_]
  r := b.clusters[_]
  q := r.clusterConfig.encryptionConfig.gcePdKmsKeyName
  q == blocked_value
  v := sprintf("Ensure that Dataproc clusters for all regions have CMEK encryptions and that the attribute exists for every Dataproc Instance", [r])
}


report := H.build_report(deny, id, title, policy_group, verification, remediation)
