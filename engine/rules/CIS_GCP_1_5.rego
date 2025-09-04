package AutoAudit_tester.rules.CIS_GCP_1_5
import data.AutoAudit_tester.engine.Helpers

result.no_admin := Helpers.status(
    Helpers.not_in_blacklist("bindings.role", {"roles/owner","roles/editor"})
)
