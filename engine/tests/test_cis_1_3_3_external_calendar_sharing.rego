package cis.microsoft_365_foundations.v6_0_0.test_control_1_3_3

import rego.v1

# ---------------------------------------------------------------------------
# Helpers: build minimal policy entries matching what the collector emits
# ---------------------------------------------------------------------------

_policy_external_disabled := {
	"name": "Default Sharing Policy",
	"domains": ["*:CalendarSharingFreeBusySimple", "Anonymous:CalendarSharingFreeBusyReviewer"],
	"enabled": false,
}

_policy_external_enabled := {
	"name": "Default Sharing Policy",
	"domains": ["*:CalendarSharingFreeBusySimple"],
	"enabled": true,
}

_second_policy_external_enabled := {
	"name": "Custom External Policy",
	"domains": ["Anonymous:CalendarSharingFreeBusyReviewer"],
	"enabled": true,
}

# ---------------------------------------------------------------------------
# Test: compliant — no sharing policies at all
# ---------------------------------------------------------------------------

test_compliant_no_policies if {
	result := data.cis.microsoft_365_foundations.v6_0_0.control_1_3_3.result with input as {"policies_allowing_external": []}
	result.compliant == true
	contains(result.message, "No sharing policies")
}

# ---------------------------------------------------------------------------
# Test: compliant — external policy exists but is disabled
# ---------------------------------------------------------------------------

test_compliant_external_policy_disabled if {
	result := data.cis.microsoft_365_foundations.v6_0_0.control_1_3_3.result with input as {"policies_allowing_external": [_policy_external_disabled]}
	result.compliant == true
	count(result.details.enabled_external_policies) == 0
}

# ---------------------------------------------------------------------------
# Test: non-compliant — one enabled policy allows external sharing
# ---------------------------------------------------------------------------

test_non_compliant_one_enabled_policy if {
	result := data.cis.microsoft_365_foundations.v6_0_0.control_1_3_3.result with input as {"policies_allowing_external": [_policy_external_enabled]}
	result.compliant == false
	count(result.details.enabled_external_policies) == 1
	contains(result.message, "1 sharing policy")
}

# ---------------------------------------------------------------------------
# Test: non-compliant — multiple enabled policies, affected resources listed
# ---------------------------------------------------------------------------

test_non_compliant_multiple_enabled_policies if {
	result := data.cis.microsoft_365_foundations.v6_0_0.control_1_3_3.result with input as {"policies_allowing_external": [_policy_external_enabled, _second_policy_external_enabled]}
	result.compliant == false
	count(result.details.enabled_external_policies) == 2
	count(result.affected_resources) == 2
}

# ---------------------------------------------------------------------------
# Test: mixed — one enabled and one disabled, only enabled counts
# ---------------------------------------------------------------------------

test_mixed_enabled_and_disabled_policies if {
	result := data.cis.microsoft_365_foundations.v6_0_0.control_1_3_3.result with input as {"policies_allowing_external": [_policy_external_disabled, _policy_external_enabled]}
	result.compliant == false
	count(result.details.enabled_external_policies) == 1
}

# ---------------------------------------------------------------------------
# Test: missing data — field absent entirely, treated as no external sharing
# ---------------------------------------------------------------------------

test_missing_policies_field if {
	result := data.cis.microsoft_365_foundations.v6_0_0.control_1_3_3.result with input as {}
	result.compliant == true
}

# ---------------------------------------------------------------------------
# Test: result structure contains expected fields
# ---------------------------------------------------------------------------

test_result_structure if {
	result := data.cis.microsoft_365_foundations.v6_0_0.control_1_3_3.result with input as {"policies_allowing_external": [_policy_external_enabled]}
	_ = result.compliant
	_ = result.message
	_ = result.affected_resources
	_ = result.details.policies_allowing_external
	_ = result.details.enabled_external_policies
}
