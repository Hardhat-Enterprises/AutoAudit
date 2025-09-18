package AutoAudit_tester.rules.CIS_GCP_2_2
import data.AutoAudit_tester.engine.Helpers as H

id           := "CIS_GCP_2_2"
title        := "Ensure That Sinks Are Configured for All Log Entries"
policy_group := "Logging and Monitoring"

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

report := H.build_report(deny, id, title, policy_group)
