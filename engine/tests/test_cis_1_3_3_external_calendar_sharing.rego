package cis.microsoft_365_foundations.v6_0_0.control_1_3_3

import rego.v1

# ---- Compliant cases ----

test_compliant_no_external_domains if {
    result := data.cis.microsoft_365_foundations.v6_0_0.control_1_3_3.result with input as {
        "sharing_policies": [
            {
                "Name": "Default Sharing Policy",
                "Enabled": true,
                "Domains": ["contoso.com:CalendarSharingFreeBusySimple"],
            }
        ]
    }
    result.compliant == true
}

test_compliant_policy_disabled if {
    result := data.cis.microsoft_365_foundations.v6_0_0.control_1_3_3.result with input as {
        "sharing_policies": [
            {
                "Name": "Default Sharing Policy",
                "Enabled": false,
                "Domains": ["*:CalendarSharingFreeBusySimple", "Anonymous:CalendarSharingFreeBusyReviewer"],
            }
        ]
    }
    result.compliant == true
}

test_compliant_no_domains if {
    result := data.cis.microsoft_365_foundations.v6_0_0.control_1_3_3.result with input as {
        "sharing_policies": [
            {
                "Name": "Default Sharing Policy",
                "Enabled": true,
                "Domains": [],
            }
        ]
    }
    result.compliant == true
}

# ---- Non-compliant cases ----

test_non_compliant_wildcard_domain if {
    result := data.cis.microsoft_365_foundations.v6_0_0.control_1_3_3.result with input as {
        "sharing_policies": [
            {
                "Name": "Default Sharing Policy",
                "Enabled": true,
                "Domains": ["*:CalendarSharingFreeBusySimple"],
            }
        ]
    }
    result.compliant == false
}

test_non_compliant_anonymous_domain if {
    result := data.cis.microsoft_365_foundations.v6_0_0.control_1_3_3.result with input as {
        "sharing_policies": [
            {
                "Name": "Default Sharing Policy",
                "Enabled": true,
                "Domains": ["Anonymous:CalendarSharingFreeBusyReviewer"],
            }
        ]
    }
    result.compliant == false
}

test_non_compliant_mixed_policies if {
    result := data.cis.microsoft_365_foundations.v6_0_0.control_1_3_3.result with input as {
        "sharing_policies": [
            {
                "Name": "Internal Only Policy",
                "Enabled": true,
                "Domains": ["contoso.com:CalendarSharingFreeBusySimple"],
            },
            {
                "Name": "Risky Policy",
                "Enabled": true,
                "Domains": ["*:CalendarSharingFreeBusySimple"],
            }
        ]
    }
    result.compliant == false
    result.details.non_compliant_policies[0].name == "Risky Policy"
}

# ---- Missing / empty data cases ----

test_no_policies_found if {
    result := data.cis.microsoft_365_foundations.v6_0_0.control_1_3_3.result with input as {
        "sharing_policies": []
    }
    result.compliant == false
}

test_missing_sharing_policies_key if {
    result := data.cis.microsoft_365_foundations.v6_0_0.control_1_3_3.result with input as {}
    result.compliant == false
}