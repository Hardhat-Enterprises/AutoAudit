# METADATA
# title: Ensure external sharing is restricted by security group
# description: |
#   Ensures only members of approved security groups can share SharePoint and
#   OneDrive content externally (GuestSharingGroupAllowListInTenantByPrincipalIdentity).
#
#   Passes only when external sharing is disabled tenant-wide
#   (SharingCapability = 0). SharingCapability is the tenant ceiling: no site
#   or OneDrive can share more openly than it allows, so nobody can share
#   externally and a group restriction adds nothing.
#
#   When groups are set, whether they are an effective restriction depends on
#   who is in them, which needs a person to judge. AutoAudit has no outcome
#   for that yet, so it fails rather than pass without the review.
# related_resources:
# - ref: https://www.cisecurity.org/benchmark/microsoft_365
#   description: CIS Microsoft 365 Foundations Benchmark
# custom:
#   control_id: CIS-7.2.8
#   framework: cis
#   benchmark: microsoft-365-foundations
#   version: v6.0.0
#   severity: medium
#   service: SharePoint
#   data_collector_id: sharepoint.pnp.tenant
#   requires_permissions:
#   - SharePoint.Admin

package cis.microsoft_365_foundations.v6_0_0.control_7_2_8

import rego.v1

default result := {
	"compliant": false,
	"message": "Unable to determine which security groups may share externally",
	"details": {},
}

allow_list := object.get(input, "guest_sharing_group_allow_list", null)

sharing_capability := object.get(input, "sharing_capability", null)

# SharingCapability is serialised as an integer enum; 0 = Disabled.
sharing_disabled if sharing_capability == 0

# Blank entries are ignored: clearing the setting can leave [""] behind.
default configured_groups := []

configured_groups := [group |
	some group in allow_list
	is_string(group)
	trim_space(group) != ""
] if {
	is_array(allow_list)
}

no_groups_set if {
	is_array(allow_list)
	count(configured_groups) == 0
}

# An unset list can be returned as null instead of [].
no_groups_set if input.guest_sharing_group_allow_list == null

result := {
	"compliant": true,
	"message": "External sharing is disabled tenant-wide, so no security group restriction is required",
	"details": {"sharing_capability": sharing_capability},
} if {
	sharing_disabled
}

result := {
	"compliant": false,
	"message": "External sharing is limited to security groups; review that their membership is restricted to approved users",
	"details": {
		"sharing_capability": sharing_capability,
		"guest_sharing_group_allow_list": configured_groups,
	},
} if {
	not sharing_disabled
	count(configured_groups) > 0
}

result := {
	"compliant": false,
	"message": "External sharing is not restricted to specific security groups",
	"details": {"sharing_capability": sharing_capability},
} if {
	not sharing_disabled
	no_groups_set
}
