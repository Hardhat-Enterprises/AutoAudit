package AutoAudit_tester.rules.CIS_GCP_2_15
import data.AutoAudit_tester.engine.Helpers as H

id           := "CIS_GCP_2_15"
title        := "Ensure 'Access Approval' is 'Enabled'"
policy_group := "Logging and Monitoring"

deny := { v |
  not has_enrolled_services
  v := sprintf("Project %q: Access Approval has no enrolled services", [input.project_id])
} ∪ { v |
  not has_notification_emails
  v := sprintf("Project %q: Access Approval has no notification/approver emails", [input.project_id])
}

has_enrolled_services {
  input.accessApproval.settings.enrolledServices
  count(input.accessApproval.settings.enrolledServices) > 0
}

has_notification_emails {
  input.accessApproval.settings.notificationEmails
  count(input.accessApproval.settings.notificationEmails) > 0
}

report := H.build_report(deny, id, title, policy_group)
