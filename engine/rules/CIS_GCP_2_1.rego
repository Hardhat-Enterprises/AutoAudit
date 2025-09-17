package AutoAudit_tester.rules.CIS_GCP_2_1
import data.AutoAudit_tester.engine.Helpers as H
id           := "CIS_GCP_2_1"
title        := "Ensure Admin Activity and Data Access logs are enabled"
policy_group := "Logging and Monitoring"

deny[v] {
  not input.logging.admin_activity_enabled
  v := sprintf("Project %q: Admin Activity logs disabled", [input.project_id])
}
deny[v] {
  not input.logging.data_access_read_enabled
  v := sprintf("Project %q: Data Access READ logs disabled", [input.project_id])
}
deny[v] {
  not input.logging.data_access_write_enabled
  v := sprintf("Project %q: Data Access WRITE logs disabled", [input.project_id])
}

report := H.build_report(deny, id, title, policy_group)

