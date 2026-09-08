# METADATA
# title: Ensure link sharing is restricted in SharePoint and OneDrive
# description: |
#   Ensure the default sharing link type presented to users in SharePoint and
#   OneDrive is "Specific people" or "Only people in your organization",
#   rather than "Anyone", so users must actively choose to widen access.
# related_resources:
# - ref: https://www.cisecurity.org/benchmark/microsoft_365
#   description: CIS Microsoft 365 Foundations Benchmark
# custom:
#   control_id: CIS-7.2.7
#   framework: cis
#   benchmark: microsoft-365-foundations
#   version: v6.0.0
#   severity: medium
#   service: SharePoint
#   data_collector_id: sharepoint.pnp.tenant
#   requires_permissions:
#   - SharePoint.Admin

package cis.microsoft_365_foundations.v6_0_0.control_7_2_7

import rego.v1

default result := {
	"compliant": false,
	"message": "Unable to determine the default sharing link type for SharePoint and OneDrive",
	"details": {},
}

# Get-PnPTenant returns DefaultSharingLinkType as the raw integer of the
# SharingLinkType enum (PnP.Core.Admin.Model.SharePoint.SharingLinkType).
# This policy owns interpreting that value rather than the collector, so
# the mapping lives in one place, next to the compliance decision it drives.
link_type_names := {
	0: "None",
	1: "Direct",
	2: "Internal",
	3: "AnonymousAccess",
}

# CIS recommends Direct (1, "Specific people") or Internal (2, "Only people
# in your organization"). AnonymousAccess (3, "Anyone with the link") is not
# compliant, and so is None (0, not configured).
default compliant := false

compliant if input.default_sharing_link_type == 1

compliant if input.default_sharing_link_type == 2

# The guard below requires default_sharing_link_type to be a number that is
# a recognised enum value (a successful link_type_names lookup) before
# evaluating compliant, so a missing/null/out-of-range collector result
# fails closed via the "unable to determine" default above instead of
# silently evaluating against undefined data.
result := output if {
	link_type := object.get(input, "default_sharing_link_type", null)
	is_number(link_type)
	link_type_name := link_type_names[link_type]

	output := {
		"compliant": compliant,
		"message": generate_message(compliant, link_type_name),
		"details": {
			"default_sharing_link_type": link_type,
			"default_sharing_link_type_name": link_type_name,
		},
	}
}

generate_message(true, link_type_name) := msg if {
	msg := sprintf(
		"Default sharing link type for SharePoint and OneDrive is '%s', which restricts sharing to specific people or the organization by default",
		[link_type_name],
	)
}

generate_message(false, link_type_name) := msg if {
	msg := sprintf(
		"Default sharing link type for SharePoint and OneDrive is '%s', which is not restricted to specific people or the organization",
		[link_type_name],
	)
}
