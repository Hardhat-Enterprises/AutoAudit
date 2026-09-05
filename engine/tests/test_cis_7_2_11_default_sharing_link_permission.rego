package cis.microsoft_365_foundations.v6_0_0.test_control_7_2_11

import rego.v1

test_compliant_view if {
    result := data.cis.microsoft_365_foundations.v6_0_0.control_7_2_11.result with input as {
        "tenant": {
            "DefaultLinkPermission": 1
        }
    }

    result.compliant == true
    contains(result.message, "set to View")
}

test_non_compliant_edit if {
    result := data.cis.microsoft_365_foundations.v6_0_0.control_7_2_11.result with input as {
        "tenant": {
            "DefaultLinkPermission": 2
        }
    }

    result.compliant == false
    contains(result.message, "instead of View")
}

test_unable_to_determine_when_null if {
    result := data.cis.microsoft_365_foundations.v6_0_0.control_7_2_11.result with input as {
        "tenant": {
            "DefaultLinkPermission": null
        }
    }

    result.compliant == false
    result.message == "Unable to determine SharePoint default sharing link permission"
}

test_unable_to_determine_when_missing if {
    result := data.cis.microsoft_365_foundations.v6_0_0.control_7_2_11.result with input as {}

    result.compliant == false
    result.message == "Unable to determine SharePoint default sharing link permission"
}
