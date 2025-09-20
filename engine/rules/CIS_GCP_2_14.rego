package AutoAudit_tester.rules.CIS_GCP_2_14
import data.AutoAudit_tester.engine.Helpers as H

id           := "CIS_GCP_2_14"
title        := "Ensure 'Access Transparency' Is Enabled (manual)"
policy_group := "Logging and Monitoring"

# Mark as manual – no API field available per CIS guidance
deny := {}

report := H.build_report(deny, id, title, policy_group)
