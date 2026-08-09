# 26T2-GRC-VH-002 — Compliance Evidence Collection Matrix

**Author:** Viet Huy Thai  
**Trimester:** T2 2026  
**Project:** AutoAudit  
**Team:** GRC  
**Artefact Type:** Compliance evidence mapping  
**Status:** Draft v0.1

---

## 1. Purpose

This document applies the evidence classification approach developed in VH-001 to real CIS Microsoft 365 controls implemented in AutoAudit.

The purpose is to identify:

- what evidence AutoAudit currently collects
- which collectors provide that evidence
- whether the evidence is direct or derived
- where evidence remains insufficient for a fully automated compliance decision
- where GRC review or further implementation is required

This matrix is based only on evidence explicitly supported by the current AutoAudit repository.

---

## 2. Scope

The initial scope covers five representative CIS Microsoft 365 Foundations v6.0.0 controls.

The controls were selected to represent different evidence situations:

1. automated user authentication evidence
2. automated Conditional Access evidence
3. privileged access governance evidence
4. Exchange audit configuration evidence
5. implemented collection where manual verification is still required

This is an initial validation sample rather than a complete mapping of all CIS Microsoft 365 controls.

---

## 3. Compliance Evidence Collection Matrix

| CIS Control | Control Area | AutoAudit Collector | Evidence Source | Direct Evidence | Derived Evidence | VH-001 Classification | Current Audit Type | GRC Limitation / Observation |
|---|---|---|---|---|---|---|---|---|
| 5.2.3.4 | Ensure all member users are MFA capable | `entra.authentication.mfa_registration_report` | Microsoft Graph API | User registration details returned from `/reports/authenticationMethods/userRegistrationDetails` | `total_users`, `mfa_registered_count`, `mfa_capable_count`, `mfa_not_registered_count`, `mfa_registration_percentage` | Raw registration data = AUTO-DIRECT; calculated counts/percentage = AUTO-DERIVED | Automated | Collector provides MFA registration and capability evidence, but final CIS pass/fail policy logic is not defined in the collector itself. |
| 5.2.2.3 | Block legacy authentication | `entra.conditional_access.legacy_auth_block` | Microsoft Graph API | Conditional Access policies | `targets_all_users`, `targets_all_apps`, `blocks_legacy_auth`, `grant_control` | Raw policies = AUTO-DIRECT; calculated flags = AUTO-DERIVED | Automated | Collector identifies relevant blocking conditions, but final CIS compliance evaluation should still be validated against the policy logic. |
| 5.3.1 | Privileged Identity Management | `entra.governance.pim_role_policies` | Microsoft Graph API | Role management policies, role definitions and policy rules | `pim_enabled`, approval requirements, MFA requirement, justification requirement, activation duration | Raw policies/rules = AUTO-DIRECT; extracted settings = AUTO-DERIVED | Automated | Presence of PIM policies does not by itself prove that every privileged role required by CIS is fully governed. |
| 3.1.1 | Microsoft 365 audit log search enabled | `exchange.organization.organization_config` | Exchange Online PowerShell | Full `Get-OrganizationConfig` result | Extracted `audit_disabled` value | Full Exchange config = AUTO-DIRECT; extracted field = AUTO-DERIVED | Automated | `controls.md` maps 3.1.1 to `AuditDisabled = False`, while the collector documentation identifies this evidence specifically with CIS 6.1.1. Mapping consistency should be reviewed. |
| 5.2.2.1 | MFA enabled for all administrative roles | `entra.conditional_access.policies` | Microsoft Graph API | Full Conditional Access policies and policy conditions | Enabled policy counts, MFA policy list and other categorised policy outputs | Raw policies = AUTO-DIRECT; categorised policy outputs = AUTO-DERIVED | Deferred | Collector is implemented, but evidence is not sufficient to confirm coverage of all 15 administrative roles. Manual/GRC verification remains required. |

---

## 4. Repository-Supported Evidence Details

### 4.1 CIS 5.2.3.4 — MFA Capable Users

The collector uses Microsoft Graph API endpoint:

`/reports/authenticationMethods/userRegistrationDetails`

Required scopes:

- `UserAuthenticationMethod.Read.All`
- `AuditLog.Read.All`

The collector returns user registration details and derives aggregate MFA values.

Important evidence fields include:

- `isMfaRegistered`
- `isMfaCapable`
- `total_users`
- `mfa_registered_count`
- `mfa_capable_count`
- `mfa_registration_percentage`

From an evidence-classification perspective, the user registration dataset is direct technical evidence, while the calculated counts and percentages are derived evidence.

---

### 4.2 CIS 5.2.2.3 — Legacy Authentication Blocking

The collector retrieves Conditional Access policies from:

`/identity/conditionalAccess/policies`

Required scope:

`Policy.Read.All`

The collector derives whether policies:

- target all users
- target all applications
- include legacy authentication client types
- apply a block grant control

Relevant derived fields include:

- `targets_all_users`
- `targets_all_apps`
- `blocks_legacy_auth`
- `grant_control`

The raw Conditional Access policies are direct evidence, while these flags are derived evidence created by AutoAudit.

---

### 4.3 CIS 5.3.1 — Privileged Identity Management

The PIM collector uses Microsoft Graph role management policy endpoints.

Required scope:

`RoleManagementPolicy.Read.Directory`

The collector retrieves:

- role management policies
- role definitions
- detailed policy rules

It then derives settings including:

- `pim_enabled`
- `global_admin_approval_required`
- `privileged_role_admin_approval_required`
- `global_admin_mfa_required`
- `global_admin_justification_required`
- `global_admin_max_activation_duration`

A key limitation is that `pim_enabled` is derived from the existence of role-management policies. Additional policy evaluation may be required to demonstrate full CIS control coverage.

---

### 4.4 CIS 3.1.1 — Audit Logging

The organization configuration collector uses Exchange Online PowerShell:

`Get-OrganizationConfig`

The collector returns the full organization configuration and extracts:

`AuditDisabled`

The control inventory states that CIS 3.1.1 should check:

`AuditDisabled = False`

However, the collector documentation associates this audit setting with CIS 6.1.1 rather than 3.1.1.

This should be reviewed for control-to-collector documentation consistency.

---

### 4.5 CIS 5.2.2.1 — Administrative MFA

The general Conditional Access collector retrieves complete Conditional Access policy configuration from Microsoft Graph.

It categorises policies by:

- enabled
- report-only
- disabled
- requiring MFA
- blocking legacy authentication
- requiring compliant devices

The collector documentation explicitly states that control 5.2.2.1 is not yet fully automatable because all administrative roles must be verified as covered.

The collector therefore provides useful technical evidence but does not yet provide sufficient evidence for a fully automated compliance decision.

---

## 5. Key GRC Findings

### VH002-F01 — Implemented collector does not always mean sufficient compliance evidence

CIS 5.2.2.1 is marked as implemented, but its audit status remains Deferred.

The repository notes that all 15 administrative roles must still be verified.

This demonstrates that:

**Collector implemented ≠ Evidence sufficient ≠ Compliance decision automated**

A collector can successfully retrieve relevant technical data while GRC review is still required to determine whether the evidence fully satisfies the control.

---

### VH002-F02 — Direct evidence and derived evidence should be distinguished

Several AutoAudit collectors return authoritative platform data and then derive additional assessment-oriented values.

Examples include:

- MFA registration records → MFA-capable counts
- Conditional Access policies → legacy-authentication flags
- PIM policy rules → approval and MFA requirement booleans
- Exchange organization configuration → extracted audit setting

This supports the VH-001 distinction between AUTO-DIRECT and AUTO-DERIVED evidence.

---

### VH002-F03 — Control-to-collector documentation inconsistency

The control inventory maps CIS 3.1.1 to `exchange.organization.organization_config` and states that `AuditDisabled = False` should be checked.

The collector documentation identifies the same audit field specifically with CIS 6.1.1.

The evidence source may still be technically reusable for both controls, but the mapping should be reviewed so that control documentation remains consistent and traceable.

---

### VH002-F04 — Deferred controls need review-state handling

The Conditional Access collector documentation states that several controls require user involvement to verify coverage, exclusions or administrative roles.

The collector comments propose a future concept similar to:

**compliant with review**

This capability is not currently implemented in the evaluation framework.

From a GRC perspective, this represents an evidence-handling gap because AutoAudit needs a way to distinguish:

- sufficient automated evidence
- insufficient automated evidence
- evidence requiring manual review
- confirmed compliance after review

---

## 6. GRC Recommendations

Based on the five reviewed controls, the following actions are recommended:

1. Maintain a distinction between direct collected evidence and derived assessment evidence.
2. Record evidence limitations where the collector cannot establish full control coverage.
3. Introduce or formalise a review-required assessment state for Deferred controls.
4. Validate final pass/fail policy logic separately from collector implementation.
5. Review control-to-collector documentation where the same evidence source supports multiple CIS controls.
6. Expand this matrix gradually as additional controls are reviewed.

---

## 7. Current Outcome

The initial Compliance Evidence Collection Matrix has been completed for five representative CIS Microsoft 365 controls.

The review identified:

- direct and derived evidence sources
- collector-level evidence fields
- evidence sufficiency limitations
- Deferred-control review requirements
- one control-mapping consistency issue
- four GRC findings for future AutoAudit improvement

This provides a practical link between collector implementation and GRC evidence requirements rather than treating collector implementation alone as proof of compliance.

---

## 8. Next Steps

Future work may include:

- validating the corresponding policy evaluation logic
- expanding the matrix to additional CIS controls
- confirming the 3.1.1 / 6.1.1 audit evidence mapping
- defining the proposed review-required status with the GRC and Engine teams
- linking these findings to the VH-003 Evidence Validation and Quality Guidelines