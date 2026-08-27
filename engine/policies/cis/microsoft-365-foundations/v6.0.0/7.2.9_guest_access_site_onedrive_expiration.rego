# METADATA
# title: Ensure guest access to a site or OneDrive will expire automatically
# description: Ensure that guest access to a SharePoint Online site or OneDrive is set to automatically expire after 30 days, per the tenant-wide external sharing settings.
# custom:
#   control_id: CIS-7.2.9
#   framework: cis
#   benchmark: microsoft-365-foundations
#   version: v6.0.0
#   severity: medium
#   service: SharePoint
#   requires_permissions:
#   - SharePoint.Admin

package cis.microsoft_365_foundations.v6_0_0.control_7_2_9

import rego.v1

default result := {
	"compliant": false,
	"message": "Unable to determine guest access expiration configuration",
	"details": {},
}

# CIS recommends ExternalUserExpirationRequired = True and
# ExternalUserExpireInDays = 30 (the tenant default is False / 60).
default compliant := false

compliant if {
	input.external_user_expiration_required == true
	input.external_user_expire_in_days == 30
}

# The guard below requires expiration_required to actually be a boolean
# (i.e. the collector ran and returned real evidence) before evaluating
# compliant, so a missing/null collector result fails closed via the
# "unable to determine" default above instead of silently evaluating
# against undefined data.
result := output if {
	is_boolean(object.get(input, "external_user_expiration_required", null))

	output := {
		"compliant": compliant,
		"message": generate_message(compliant),
		"details": {
			"external_user_expiration_required": input.external_user_expiration_required,
			"external_user_expire_in_days": object.get(input, "external_user_expire_in_days", null),
		},
	}
}

generate_message(true) := "Guest access to SharePoint sites and OneDrive is set to expire automatically after 30 days"

generate_message(false) := "Guest access to SharePoint sites and OneDrive is not set to expire after exactly 30 days (expiration is disabled or set to a different number of days)"