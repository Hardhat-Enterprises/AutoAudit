package AutoAudit_tester.engine.Helpers

import future.keywords.in

to_array(xs) = arr if {
  arr := [x | x := xs[_]]
}

status(pass) := "Compliant"   if  { pass }
status(pass) := "NonCompliant" if { not pass }

build_report(deny_items, id, title, input_kind, verification, remediation) = report if {
  ds := to_array(deny_items)
  report := {
    "id":         id,
    "title":      title,
    "input_kind": input_kind,
    "status":     status(count(ds) == 0),
    "counts":     {"violations": count(ds)},
    "violations": ds,
    "verification": verification,
    "remediation": remediation
  }
}