package cis.microsoft_365_foundations.v6_0_0.control_7_2_4

import rego.v1

default result := {
    "compliant": false,
    "message": "Evaluation failed: unable to verify SharePoint tenant sharing capability",
    "details": {},
}

# SharingCapability = 2 (ExternalUserAndGuestSharing) is the only non-compliant value.
# 0 = Disabled, 1 = ExternalUserSharingOnly, 3 = ExistingExternalUserSharingOnly are all restricted.
NON_COMPLIANT_VALUE := 2

sharing_capability := object.get(input, "sharing_capability", null)

result := {
    "compliant": true,
    "message": sprintf("OneDrive/SharePoint sharing is restricted (SharingCapability = %v).", [sharing_capability]),
    "details": {"sharing_capability": sharing_capability},
} if {
    sharing_capability != null
    sharing_capability != NON_COMPLIANT_VALUE
}

result := {
    "compliant": false,
    "message": "OneDrive/SharePoint sharing capability is set to allow anyone, including anonymous links (SharingCapability = 2).",
    "details": {"sharing_capability": sharing_capability},
} if {
    sharing_capability == NON_COMPLIANT_VALUE
}

result := {
    "compliant": false,
    "message": "SharingCapability value missing from evidence; unable to verify.",
    "details": {},
} if {
    sharing_capability == null
}