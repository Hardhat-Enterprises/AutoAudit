# CIS M365 v6.0.0 — Manual Control Classification

## Purpose

AutoAudit scans Microsoft 365 tenants automatically and checks them
against the CIS M365 Foundations Benchmark v6.0.0. But not every
control can be checked by code. Some settings have no API, some live
in admin portals that only a human can open, and some require a
judgment call that a script cannot make.

This document lists the 14 controls that fall into that category,
explains why each one cannot be automated right now, and specifies
what an auditor needs to provide as evidence.

Each row in the control register below maps directly to one record in
the ControlVerificationTemplate table that the backend builds.
Without this classification, that table has no content and auditors
have no guidance when they open a pending manual control.

## Two sub-categories

Not all 14 controls are manual for the same reason. It helps to split
them into two groups.

**Truly manual — no API exists:**
1.1.2, 1.3.8, 2.2.1, 2.4.3, 5.1.2.1, 5.1.2.4, 5.1.2.5, 5.1.2.6,
5.1.8.1, 5.2.4.1, 8.4.1

These settings either have no public API at all, are only available
through internal Microsoft APIs that app registrations cannot reach,
or require a human policy decision that cannot be expressed as a
configuration value. They will remain manual until Microsoft exposes
the relevant API surface.

**Manually verified for now — automation candidates:**
- **7.2.8** — The SharePoint collector exists in the AutoAudit
  codebase but is incomplete and raises `NotImplementedError` when
  called. CIS actually marks this control as potentially automatable.
  Once a developer finishes the collector, this control can move from
  manual to automated with no changes needed to the template table.
- **9.1.1–9.1.12** — Microsoft Fabric does have a tenant settings
  API. The blocker is that AutoAudit has not yet confirmed that
  app-only authentication works against Fabric admin endpoints. Until
  that is tested and working, auditors verify these 12 controls
  manually. They are the most likely controls to be automated next.

## Control register

| control_id | severity | service | why manual | evidence_type |
|---|---|---|---|---|
| 1.1.2 | high | EntraID | Which accounts are designated as break-glass is an organisational policy decision, not a config value any API can read | screenshot |
| 1.3.8 | medium | Sway | Microsoft provides no API for Sway external sharing settings | screenshot |
| 2.2.1 | high | EntraID | Defining which accounts to monitor is a human decision, there is no API that can confirm this is set up correctly | screenshot |
| 2.4.3 | medium | Defender | MCAS configuration must be verified through the security portal , no stable API exposes its enabled state and policy configuration | screenshot |
| 5.1.2.1 | medium | EntraID | The relevant endpoint only exists in the Microsoft Graph beta API, which is not stable enough for production use | screenshot |
| 5.1.2.4 | medium | EntraID | This setting is only accessible through an internal Azure API that is not available to app registrations | screenshot |
| 5.1.2.5 | low | EntraID | Microsoft does not expose this setting through the Graph API | screenshot |
| 5.1.2.6 | low | EntraID | Same as 5.1.2.4 — internal Azure API only, no app registration access | screenshot |
| 5.1.8.1 | high | EntraID | Verifying password hash sync requires checking on-premises AD Connect directly, there is no cloud API for this | screenshot |
| 5.2.4.1 | medium | EntraID | SSPR settings are not exposed through the Graph API | screenshot |
| 7.2.8 | medium | SharePoint | The collector exists but raises NotImplementedError, automation candidate once the collector is completed | screenshot |
| 8.4.1 | medium | Teams | CIS marks this as manual; Teams app permission policy configuration is only accessible through the Teams admin portal | screenshot |
| 9.1.1–9.1.12 | medium | Fabric | Fabric API auth is untested in AutoAudit, automation candidates once Fabric app-only auth is confirmed working | screenshot |

## Notes on the automation candidates

**7.2.8 — SharePoint external sharing:**
The `sharepoint.spo_tenant` collector is already registered in
AutoAudit but the implementation is not finished. A developer raising
a `NotImplementedError` is a placeholder, not a permanent blocker.
Once someone completes the collector, this control slots straight into
the automated scan with no other changes needed. The template provided
here covers the interim period.

**9.1.1–9.1.12 — Fabric tenant settings:**
These twelve controls all live in the same place, the Fabric admin
portal under Tenant settings. Microsoft does have an API for this,
which is why these controls are marked as candidates rather than
permanently manual. The problem is that AutoAudit has not yet
validated that its app registration can authenticate against the
Fabric admin endpoints. Once that is confirmed, all twelve controls
can be automated in one go. Until then, auditors use the templates
in this document to verify them manually through the portal.