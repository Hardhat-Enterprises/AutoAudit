package AutoAudit_tester.rules.CIS_GCP_4_6
import data.AutoAudit_tester.engine.Helpers as H

id    := "CIS_GCP_4_6"
title := "Ensure That IP Forwarding Is Not Enabled on Instances"
policy_group := "Compute"
blocked_value := "true"

deny := { v |
  b := input[_]
  r := b.canIpForward
  r == blocked_value
  v := sprintf("Compute instance should ensure that IP Forwarding is administratively disabled and the canIpForward attribute should not be set to: %q", [r])
}

report := H.build_report(deny, id, title, policy_group)
