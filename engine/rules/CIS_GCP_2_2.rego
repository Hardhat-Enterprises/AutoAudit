package AutoAudit_tester.rules.CIS_GCP_2_2
import data.AutoAudit_tester.engine.Helpers as H

id           := "CIS_GCP_2_2"
title        := "Ensure That Sinks Are Configured for All Log Entries"
policy_group := "Logging and Monitoring"

verification := `1. Ensure that a sink with an empty filter exists. List the sinks for the project,
folder or organization. If sinks are configured at a folder or organization level,
they do not need to be configured for each project:
gcloud logging sinks list --folder=FOLDER_ID | --organization=ORGANIZATION_ID
| --project=PROJECT_ID
The output should list at least one sink with an empty filter.
2. Additionally, ensure that the resource configured as Destination exists.`

remediation := `To create a sink to export all log entries in a Google Cloud Storage bucket:
gcloud logging sinks create <sink-name>
storage.googleapis.com/DESTINATION_BUCKET_NAME
Sinks can be created for a folder or organization, which will include all projects.
gcloud logging sinks create <sink-name>
storage.googleapis.com/DESTINATION_BUCKET_NAME --include-children --
folder=FOLDER_ID | --organization=ORGANIZATION_ID`

# Require at least one sink with EMPTY filter and a valid destination
deny := { v |
  not some_sink_catches_all
  v := sprintf("Project %q: No Logs Router sink exports ALL entries to a valid destination", [input.project_id])
}

some_sink_catches_all {
  some s
  s := input.logging.sinks[_]
  (not s.filter) or s.filter == ""   # inclusion filter empty
  s.destination != ""                # destination exists
}

report := H.build_report(deny, id, title, policy_group, verification, remediation)
