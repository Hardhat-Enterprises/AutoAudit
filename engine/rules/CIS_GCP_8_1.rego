package AutoAudit_tester.rules.CIS_GCP_7_1
import data.AutoAudit_tester.engine.Helpers as H

id    := "CIS_GCP_7_1"
title := "Ensure BigQuery datasets are not anonymously/publicly accessible"
policy_group := "BigQuery"
blocked_value := ["allUsers", "allAuthenticatedUsers"]

deny := { v |  
  b := input[_]
  r := b.access[_]
  q := r.specialGroup
  q in blocked_value
  v := sprintf("Ensure that users are not granted the role of %q or %q and that the attribute is not set to a value: %q for a BigQuery Instances", [blocked_value[0], blocked_value[1], q])
}


report := H.build_report(deny, id, title, policy_group)
