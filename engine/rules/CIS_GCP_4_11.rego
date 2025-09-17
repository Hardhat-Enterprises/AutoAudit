package AutoAudit_tester.rules.CIS_GCP_4_11
import data.AutoAudit_tester.engine.Helpers as H

id    := "CIS_GCP_4_11"
title := "Ensure That Compute Instances Have Confidential Computing Enabled"
policy_group := "Compute"
blocked_value := false

deny := { v |  
  b := input[_]
  r := b.confidentialInstanceConfig.enableConfidentialCompute
  q := b.confidentialInstanceConfig.confidentialInstanceType
  startswith(q, "n2d")
  r.accessConfigs == blocked_value
  v := sprintf("Compute instance should ensure that there is no Confidential Computing is enabled and the enableConfidentialCompute attribute should be set to: %q for every n2d machine instance", [blocked_value])
}


report := H.build_report(deny, id, title, policy_group)
