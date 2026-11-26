# METADATA
# title: Ensure multifactor authentication is enabled for all users
# description: |
#   Requires that at least one enabled Conditional Access policy enforces MFA
#   for all users across all cloud applications.
#
#   Excluding Microsoft Rights Management Services is allowed, because CIS
#   recommends it. A policy that excludes any other cloud app, by list or by
#   filter, does not count. Whether those exclusions are justified, or the
#   apps are covered by another policy, needs a person to judge. AutoAudit has
#   no outcome for that yet, so it fails rather than pass without the review.
#
#   User, group and role exclusions (e.g. break-glass accounts) are common and
#   legitimate, so their presence is surfaced as evidence for assessor review
#   rather than treated as an automatic fail.
# related_resources:
# - ref: https://www.cisecurity.org/benchmark/microsoft_365
#   description: CIS Microsoft 365 Foundations Benchmark
# - ref: https://learn.microsoft.com/en-us/graph/api/resources/conditionalaccesspolicy
#   description: Conditional Access policies - Microsoft Graph API
# custom:
#   control_id: CIS-5.2.2.2
#   framework: cis
#   benchmark: microsoft-365-foundations
#   version: v6.0.0
#   severity: critical
#   service: EntraID
#   requires_permissions:
#   - Policy.Read.All

package cis.microsoft_365_foundations.v6_0_0.control_5_2_2_2

import rego.v1

default result := {
    "compliant": false,
    "message": "Evaluation failed: unable to retrieve Conditional Access policy data",
    "details": {},
}

targets_all_users(p) if {
    "All" in p.conditions.users.includeUsers
}

targets_all_apps(p) if {
    "All" in p.conditions.applications.includeApplications
}

# CIS recommends excluding Microsoft Rights Management Services so external
# users can still open documents protected with sensitivity labels.
allowed_excluded_apps := {"00000012-0000-0000-c000-000000000000"}

excluded_apps(p) := {app | some app in object.get(p.conditions.applications, "excludeApplications", [])}

# Apps can also be excluded by a filter (e.g. on custom security attributes).
excludes_apps_by_filter(p) if {
    p.conditions.applications.applicationFilter.mode == "exclude"
}

excludes_any_app(p) if count(excluded_apps(p)) > 0

excludes_any_app(p) if excludes_apps_by_filter(p)

exclude_filter_rule(p) := p.conditions.applications.applicationFilter.rule if {
    excludes_apps_by_filter(p)
} else := null

# Any other excluded app might be justified or covered by another policy,
# which the engine can't tell, so it needs a human to review it.
needs_app_review(p) if {
    count(excluded_apps(p) - allowed_excluded_apps) > 0
}

needs_app_review(p) if {
    excludes_apps_by_filter(p)
}

policy_label(p) := p.displayName if {
    is_string(p.displayName)
} else := p.id if {
    is_string(p.id)
} else := "unnamed policy"

all_users_all_apps_policies := [p |
    some p in input.policies_requiring_mfa
    p.state == "enabled"
    targets_all_users(p)
    targets_all_apps(p)
]

# A policy that needs app review doesn't count toward a pass.
qualifying_policies := [p |
    some p in all_users_all_apps_policies
    not needs_app_review(p)
]

policies_needing_app_review := [p |
    some p in all_users_all_apps_policies
    needs_app_review(p)
]

app_exclusions := [{
    "policy_id": object.get(p, "id", null),
    "policy_name": object.get(p, "displayName", null),
    "excluded_apps": sort(excluded_apps(p)),
    "exclude_filter_rule": exclude_filter_rule(p),
    "counts_toward_pass": p in qualifying_policies,
} |
    some p in all_users_all_apps_policies
    excludes_any_app(p)
]

has_exclusions(p) if {
    count(object.get(p.conditions.users, "excludeUsers", [])) > 0
}

has_exclusions(p) if {
    count(object.get(p.conditions.users, "excludeGroups", [])) > 0
}

has_exclusions(p) if {
    count(object.get(p.conditions.users, "excludeRoles", [])) > 0
}

policies_with_exclusions := [p.displayName |
    some p in qualifying_policies
    has_exclusions(p)
]

result := output if {
    count(qualifying_policies) > 0

    output := {
        "compliant": true,
        "message": sprintf(
            "MFA is required for all users via %d Conditional Access policy(ies)",
            [count(qualifying_policies)],
        ),
        "details": {
            "qualifying_policy_names": [p.displayName | some p in qualifying_policies],
            "policies_with_exclusions": policies_with_exclusions,
            "exclusions_detected": count(policies_with_exclusions) > 0,
            "app_exclusions": app_exclusions,
            "total_policies_requiring_mfa": count(input.policies_requiring_mfa),
        },
    }
}

# User, group and role exclusions on policies that don't count aren't shown
# here yet. Deferred to 26T3-ENG-TEAM-020, which reviews those exclusions.
fail_details := {
    "qualifying_policy_names": [],
    "policies_with_exclusions": [],
    "exclusions_detected": false,
    "app_exclusions": app_exclusions,
    "total_policies_requiring_mfa": count(input.policies_requiring_mfa),
}

# No policy qualifies, but some would if not for their app exclusions. They
# need a person to review them, so this branch becomes indeterminate once the
# result contract supports it.
result := output if {
    count(qualifying_policies) == 0
    count(policies_needing_app_review) > 0

    output := {
        "compliant": false,
        "message": sprintf(
            "MFA policies for all users were not counted because they exclude cloud apps other than Microsoft Rights Management Services; review whether those exclusions are justified: %s",
            [concat(", ", [policy_label(p) | some p in policies_needing_app_review])],
        ),
        "details": fail_details,
    }
}

result := output if {
    count(qualifying_policies) == 0
    count(policies_needing_app_review) == 0

    output := {
        "compliant": false,
        "message": "No enabled Conditional Access policy requires MFA for all users across all cloud apps",
        "details": fail_details,
    }
}
