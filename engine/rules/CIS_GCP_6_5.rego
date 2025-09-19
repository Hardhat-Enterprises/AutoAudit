package AutoAudit_tester.rules.CIS_GCP_6_5
import data.AutoAudit_tester.engine.Helpers as H

id    := "CIS_GCP_6_5"
title := "Ensure Cloud SQL does not implicitly whitelist all public IPs"
policy_group := "Cloud SQL"
blocked_value := "0.0.0.0/0"

deny := { v |  
  b := input[_]
  r := b.settings.ipConfiguration.authorizedNetworks[_]
  q := r.value
  q == blocked_value
  v := sprintf("Ensure that only validated networks are allowed to connect to the SQL server and that the attribute is never set to a value: %q for a SQLserver Instances", [blocked_value])
}


report := H.build_report(deny, id, title, policy_group)
