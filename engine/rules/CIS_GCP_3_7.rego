package AutoAudit_tester.rules.CIS_GCP_3_7
import data.AutoAudit_tester.engine.Helpers as H
import future.keywords.in

id    := "CIS_GCP_3_7"
title := "Ensure That RDP Access Is Restricted From the Internet"
policy_group := "Networking"
blocked_value1 := ["0.0.0.0/0"]
blocked_value2 := "INGRESS"
blocked_value3 := ["tcp", "ALL"]
blocked_value4 := ["3389", "Null"]

deny := { v |  
  b := input[_]
  r := b.sourceRanges
  q := b.direction
  a := b.allowed[_]
  c := a.IPProtocol
  d := a.ports[_]

  r == blocked_value1
  q == blocked_value2
  c in blocked_value3
  d in blocked_value4

  v := sprintf("generic connections on port/s %q from IP ranges %q coming in the %q direction using protocol %q should be avoided", [blocked_value4, blocked_value1, blocked_value3, blocked_value2])
}


report := H.build_report(deny, id, title, policy_group)
