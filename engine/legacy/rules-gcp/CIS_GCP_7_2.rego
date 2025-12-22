package AutoAudit_tester.rules.CIS_GCP_7_2
import data.AutoAudit_tester.engine.Helpers as H

id    := "CIS_GCP_7_2"
title := "Ensure all BigQuery tables are encrypted with CMEK's"
policy_group := "BigQuery"
blocked_value := ""

verification := `List all dataset names
bq ls
Use the following command to view the table details. Verify the kmsKeyName is present.
bq show <table_object>`

remediation := `Use the following command to copy the data. The source and the destination needs to
be same in case copying to the original table.
bq cp --destination_kms_key <customer_managed_key>
source_dataset.source_table destination_dataset.destination_table`

deny := { v |  
  b := input[_]
  r := b.tables[_]
  q := r.encryptionConfiguration.kmsKeyName
  q == blocked_value
  v := sprintf("Ensure that BigQuery tables are all encrypted using customer managed encryption and that the attribute exists for a BigQuery Instances", [r])
}


report := H.build_report(deny, id, title, policy_group, verification, remediation)
