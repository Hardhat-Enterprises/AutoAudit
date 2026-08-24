package cis.microsoft_365_foundations.v6_0_0.control_1_3_9

import rego.v1

default result := {
    "compliant": false,
    "message": "Unable to determine Bookings configuration",
    "details": {}
}

# CIS 1.3.9: Ensure shared bookings pages are restricted to select users
# Compliant if:
#   - Default OWA policy has BookingsMailboxCreationEnabled = false, OR
#   - Organization-level BookingsEnabled = false

# Compliant case 1: Default OWA policy has bookings disabled
result := output if {
    input.owa_mailbox_policy.default_policy_bookings_mailbox_creation_enabled == false
    
    output := {
        "compliant": true,
        "message": "Shared Bookings is appropriately restricted",
        "details": {
            "default_policy_bookings_mailbox_creation_enabled": input.owa_mailbox_policy.default_policy_bookings_mailbox_creation_enabled,
            "bookings_enabled": input.owa_mailbox_policy.bookings_enabled,
        }
    }
}

# Compliant case 2: Org-level bookings disabled
result := output if {
    input.owa_mailbox_policy.bookings_enabled == false
    
    output := {
        "compliant": true,
        "message": "Shared Bookings is appropriately restricted",
        "details": {
            "default_policy_bookings_mailbox_creation_enabled": input.owa_mailbox_policy.default_policy_bookings_mailbox_creation_enabled,
            "bookings_enabled": input.owa_mailbox_policy.bookings_enabled,
        }
    }
}

# Non-compliant case: Both enabled
result := output if {
    input.owa_mailbox_policy.default_policy_bookings_mailbox_creation_enabled == true
    input.owa_mailbox_policy.bookings_enabled == true
    
    output := {
        "compliant": false,
        "message": "Shared Bookings is enabled and not restricted to select users",
        "details": {
            "default_policy_bookings_mailbox_creation_enabled": input.owa_mailbox_policy.default_policy_bookings_mailbox_creation_enabled,
            "bookings_enabled": input.owa_mailbox_policy.bookings_enabled,
        }
    }
}