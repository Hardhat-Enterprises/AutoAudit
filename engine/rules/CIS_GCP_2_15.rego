package AutoAudit_tester.rules.CIS_GCP_2_15
import data.AutoAudit_tester.engine.Helpers as H

id           := "CIS_GCP_2_15"
title        := "Ensure 'Access Approval' is 'Enabled'"
policy_group := "Logging and Monitoring"

verification := `1. From within the project you wish to audit, run the following command.
gcloud access-approval settings get
2. The status will be displayed in the output.
IF Access Approval is not enabled you should get this output:
API [accessapproval.googleapis.com] not enabled on project [-----]. Would you
like to enable and retry (this will take a few minutes)? (y/N)?
After entering Y if you get the following output, it means that Access Transparency is
not enabled:
ERROR: (gcloud.access-approval.settings.get) FAILED_PRECONDITION:
Precondition check failed.`

remediation := `1. To update all services in an entire project, run the following command from an
account that has permissions as an 'Approver for Access Approval Requests'
gcloud access-approval settings update --project=<project name> --
enrolled_services=all --notification_emails='<email recipient for access
approval requests>@<domain name>'`

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

report := H.build_report(deny, id, title, policy_group, verification, remediation)
