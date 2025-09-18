package AutoAudit_tester.rules.CIS_GCP_6_6
import data.AutoAudit_tester.engine.Helpers as H

id    := "CIS_GCP_6_6"
title := "Ensure Cloud SQL instances do not have public IPs"
policy_group := "Cloud SQL"
blocked_value := True

deny := { v |  
  b := input[_]
  r := b.settings.ipConfiguration.ipv4Enabled
  r == blocked_value
  v := sprintf("Ensure that Public Ipv4 is not allocated to a database to reduce attack surface and that the attribute is never set to a value: %q for a SQLserver Instances", [blocked_value])
}


report := H.build_report(deny, id, title, policy_group)
