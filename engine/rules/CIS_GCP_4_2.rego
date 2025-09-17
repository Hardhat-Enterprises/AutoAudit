package AutoAudit_tester.rules.CIS_GCP_4_2
import data.AutoAudit_tester.engine.Helpers as H

id    := "CIS_GCP_4_2"
title := "Ensure That Instances Are Not Configured To Use the Default Service Account With Full Access to All Cloud APIs"
policy_group := "Compute"
blocked_value := "Company_Name"

deny := { v |
  b := input[_]
  r := b.serviceAccounts.email
  startswith(r, blocked_value)
  v := sprintf("Compute instance should not use default Compute engine service accounts like %q", [r])
}

report := H.build_report(deny, id, title, policy_group)
