package cis.microsoft_365_foundations.v6_0_0.test_control_2_1_5

import rego.v1

# A policy with all three settings the way CIS 2.1.5 requires.
good_policy := {
    "Name": "Default",
    "EnableATPForSPOTeamsODB": true,
    "EnableSafeDocs": true,
    "AllowSafeDocsOpen": false,
}

test_compliant_all_three_settings_correct if {
    result := data.cis.microsoft_365_foundations.v6_0_0.control_2_1_5.result with input as {"atp_policy": good_policy}
    result.compliant == true
}

test_noncompliant_all_three_settings_wrong if {
    result := data.cis.microsoft_365_foundations.v6_0_0.control_2_1_5.result with input as {"atp_policy": {
        "Name": "Default",
        "EnableATPForSPOTeamsODB": false,
        "EnableSafeDocs": false,
        "AllowSafeDocsOpen": true,
    }}
    result.compliant == false
}

# Logic bug: any ONE wrong setting must fail.
test_noncompliant_only_atp_for_spo_teams_odb_disabled if {
    result := data.cis.microsoft_365_foundations.v6_0_0.control_2_1_5.result with input as {"atp_policy": object.union(good_policy, {"EnableATPForSPOTeamsODB": false})}
    result.compliant == false
}

test_noncompliant_only_safe_docs_disabled if {
    result := data.cis.microsoft_365_foundations.v6_0_0.control_2_1_5.result with input as {"atp_policy": object.union(good_policy, {"EnableSafeDocs": false})}
    result.compliant == false
}

test_noncompliant_only_allow_safe_docs_open_enabled if {
    result := data.cis.microsoft_365_foundations.v6_0_0.control_2_1_5.result with input as {"atp_policy": object.union(good_policy, {"AllowSafeDocsOpen": true})}
    result.compliant == false
}

# Missing evidence must fail, not pass.
test_noncompliant_empty_cmdlet_output if {
    result := data.cis.microsoft_365_foundations.v6_0_0.control_2_1_5.result with input as {"atp_policy": {}}
    result.compliant == false
}

test_noncompliant_missing_atp_policy if {
    result := data.cis.microsoft_365_foundations.v6_0_0.control_2_1_5.result with input as {}
    result.compliant == false
}

test_noncompliant_null_atp_policy if {
    result := data.cis.microsoft_365_foundations.v6_0_0.control_2_1_5.result with input as {"atp_policy": null}
    result.compliant == false
}
