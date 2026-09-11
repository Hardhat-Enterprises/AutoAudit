package m365.exchange.audit_log_search_enabled

# CIS Microsoft 365 Foundations v6.0.0
# Control 3.1.1: Ensure Microsoft 365 audit log search is Enabled
# Data Collector: exchange.organization.organization_config
# Field: audit_disabled

import future.keywords.if
import future.keywords.in

default allow := false

field_exists if {
    is_boolean(input.audit_disabled)
}

allow if {
    input.audit_disabled == false
}
# VIOLATION 1: audit is explicitly disabled
violation[{"msg": msg, "control_id": control_id}] if {
    input.audit_disabled == true
    msg := "Organization-wide audit log search is disabled (audit_disabled = true)."
    control_id := "3.1.1"
}
# VIOLATION 2: field missing
violation[{"msg": msg, "control_id": control_id}] if {
    not field_exists
    msg := "audit_disabled property is missing from collector output."
    control_id := "3.1.1"
}