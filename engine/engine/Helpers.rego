package AutoAudit_tester.engine.Helpers

import future.keywords.in

get(path) = v if {
  parts := split(path, ".")
  some i
  pv := walk(input)[i]
  p := pv[0]
  v := pv[1]
  p == parts
}
equals(path, expected) if {
  get(path) == expected
}

in_whitelist(path, allowed) if {
  val := get(path)
  val in allowed
}
not_in_blacklist(path, blocked) if {
  val := get(path)
  not val in blocked
}
status(bool) = s if {
  bool
  s := "Compliant"
}
status(bool) = s if {
  not bool
  s := "NonCompliant"
}
