package AutoAudit_tester.rules.CIS_GCP_2_13
import data.AutoAudit_tester.engine.Helpers as H

id           := "CIS_GCP_2_13"
title        := "Ensure Cloud Asset Inventory Is Enabled"
policy_group := "Logging and Monitoring"

deny := { v |
  not cloud_asset_api_enabled
  v := sprintf("Project %q: Cloud Asset API (cloudasset.googleapis.com) is not enabled", [input.project_id])
}

cloud_asset_api_enabled {
  some s
  s := input.services[_].name
  s == "cloudasset.googleapis.com"
}

report := H.build_report(deny, id, title, policy_group)
