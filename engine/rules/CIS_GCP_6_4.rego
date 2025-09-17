package AutoAudit_tester.rules.CIS_GCP_6_4
import data.AutoAudit_tester.engine.Helpers as H

id    := "CIS_GCP_6_4"
title := "Ensure Cloud SQL requires SSL for all incoming connections"
policy_group := "Cloud SQL"
blocked_value := "True"

deny := { v |  
  b := input[_]
  r := b.settings.ipConfiguration.requireSsl
  r != blocked_value
  v := sprintf("Ensure that all incoming connections to the database are enforced with SSL and that the attribute is set to a value: %q for a SQLserver Instances", [blocked_value])
}


report := H.build_report(deny, id, title, policy_group)
