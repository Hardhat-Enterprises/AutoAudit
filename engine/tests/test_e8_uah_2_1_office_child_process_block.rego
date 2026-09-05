package essential_eight.asd_essential_eight.v2025.test_e8_uah_2_1

import rego.v1

test_compliant_block_mode if {
    result := data.essential_eight.asd_essential_eight.v2025.control_e8_uah_2_1.result with input as {
        "office_child_process_rule_state": "block",
        "office_child_process_rule_found": true,
        "office_child_process_source": "legacy_endpoint_protection",
        "office_child_process_policy_name": "Baseline Endpoint Protection",
    }
    result.compliant == true
    result.details.source == "legacy_endpoint_protection"
}

test_non_compliant_audit_mode if {
    result := data.essential_eight.asd_essential_eight.v2025.control_e8_uah_2_1.result with input as {
        "office_child_process_rule_state": "audit",
        "office_child_process_rule_found": true,
        "office_child_process_source": "legacy_endpoint_protection",
        "office_child_process_policy_name": "Baseline Endpoint Protection",
    }
    result.compliant == false
    result.details.office_child_process_rule_state == "audit"
}

test_non_compliant_rule_not_configured if {
    result := data.essential_eight.asd_essential_eight.v2025.control_e8_uah_2_1.result with input as {
        "office_child_process_rule_state": "not_configured",
        "office_child_process_rule_found": false,
        "office_child_process_source": null,
        "office_child_process_policy_name": null,
    }
    result.compliant == false
    result.details.office_child_process_rule_found == false
}
