package AutoAudit_tester.rules.CIS_GCP_2_1
import data.AutoAudit_tester.engine.Helpers as H
id           := "CIS_GCP_2_1"
title        := "Ensure Admin Activity and Data Access logs are enabled"
policy_group := "Logging and Monitoring"

verification := ` 1. List the Identity and Access Management (IAM) policies for the project, folder, or
organization:
gcloud organizations get-iam-policy ORGANIZATION_ID
gcloud resource-manager folders get-iam-policy FOLDER_ID
gcloud projects get-iam-policy PROJECT_ID
2. Policy should have a default auditConfigs section which has the logtype set to
DATA_WRITES and DATA_READ for all services. Note that projects inherit
settings from folders, which in turn inherit settings from the organization. When
called, projects get-iam-policy, the result shows only the policies set in the
project, not the policies inherited from the parent folder or organization.
Nevertheless, if the parent folder has Cloud Audit Logging enabled, the project
does as well.
Sample output for default audit configs may look like this:
auditConfigs:
- auditLogConfigs:
- logType: ADMIN_READ
- logType: DATA_WRITE
- logType: DATA_READ
service: allServices
3. Any of the auditConfigs sections should not have parameter
"exemptedMembers:" set, which will ensure that Logging is enabled for all users
and no user is exempted. `

remediation := ` 1. To read the project's IAM policy and store it in a file run a command:
gcloud projects get-iam-policy PROJECT_ID > /tmp/project_policy.yaml
Alternatively, the policy can be set at the organization or folder level. If setting the policy
at the organization level, it is not necessary to also set it for each folder or project.
gcloud organizations get-iam-policy ORGANIZATION_ID > /tmp/org_policy.yaml
gcloud resource-manager folders get-iam-policy FOLDER_ID >
/tmp/folder_policy.yaml
2. Edit policy in /tmp/policy.yaml, adding or changing only the audit logs
configuration to:
Note: Admin Activity Logs are enabled by default, and cannot be disabled.
So they are not listed in these configuration changes.
auditConfigs:
- auditLogConfigs:
- logType: DATA_WRITE
- logType: DATA_READ
service: allServices
Note: exemptedMembers: is not set as audit logging should be enabled for all the users
3. To write new IAM policy run command:
gcloud organizations set-iam-policy ORGANIZATION_ID /tmp/org_policy.yaml
gcloud resource-manager folders set-iam-policy FOLDER_ID
/tmp/folder_policy.yaml
gcloud projects set-iam-policy PROJECT_ID /tmp/project_policy.yaml
If the preceding command reports a conflict with another change, then repeat these
steps, starting with the first step. `

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

report := H.build_report(deny, id, title, policy_group, verification, remediation)

