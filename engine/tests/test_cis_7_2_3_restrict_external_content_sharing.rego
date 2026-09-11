package cis.microsoft_365_foundations.v6_0_0.test_control_7_2_3

import rego.v1

test_compliant_disabled if {
    result := data.cis.microsoft_365_foundations.v6_0_0.control_7_2_3.result with input as {
        "tenant": {
            "SharingCapability": 0
        }
    }

    result.compliant == true
    contains(result.message, "disabled")
}

test_compliant_external_users_only if {
    result := data.cis.microsoft_365_foundations.v6_0_0.control_7_2_3.result with input as {
        "tenant": {
            "SharingCapability": 1
        }
    }

    result.compliant == true
    contains(result.message, "authenticated external users")
}

test_compliant_existing_external_users_only if {
    result := data.cis.microsoft_365_foundations.v6_0_0.control_7_2_3.result with input as {
        "tenant": {
            "SharingCapability": 3
        }
    }

    result.compliant == true
    contains(result.message, "existing external users")
}

test_non_compliant_external_and_guest_sharing if {
    result := data.cis.microsoft_365_foundations.v6_0_0.control_7_2_3.result with input as {
        "tenant": {
            "SharingCapability": 2
        }
    }

    result.compliant == false
    contains(result.message, "guest sharing")
}

test_unable_to_determine_when_null if {
    result := data.cis.microsoft_365_foundations.v6_0_0.control_7_2_3.result with input as {
        "tenant": {
            "SharingCapability": null
        }
    }

    result.compliant == false
    result.message == "Unable to determine SharePoint external sharing capability"
}

test_unable_to_determine_when_missing if {
    result := data.cis.microsoft_365_foundations.v6_0_0.control_7_2_3.result with input as {}

    result.compliant == false
    result.message == "Unable to determine SharePoint external sharing capability"
}
