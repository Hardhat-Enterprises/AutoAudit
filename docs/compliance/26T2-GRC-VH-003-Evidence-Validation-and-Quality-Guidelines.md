# VH-003: Evidence Validation and Quality Guidelines

**Project:** AutoAudit  
**Team:** GRC  
**Artefact type:** Evidence validation guidance  
**Status:** Draft for review  
**Benchmark:** CIS Microsoft 365 Foundations Benchmark v6.0.0  
**Reviewed main baseline:** `90e4217933e00ab52b47c9667d4093b6f1276292`  
**Validation basis:** Repository source inspection. No live-tenant testing was performed for this review.

## 1. Purpose and scope

These guidelines help AutoAudit contributors and reviewers determine whether compliance evidence is available, traceable, complete, correctly transformed, and sufficient for assessment.

The central distinction is:

> Evidence collected ≠ evidence complete ≠ compliance established

AutoAudit can declare a collector without implementing it, derive a coverage flag without retaining all relevant context, or return configuration that still requires organizational verification. A successful collection operation therefore does not, by itself, justify a compliance conclusion.

VH-003 builds on the direct and derived evidence distinction used in VH-001 and the control mappings examined in VH-002. Its scope is the collection and evaluation of CIS Microsoft 365 Foundations Benchmark v6.0.0 evidence.

Three evidence labels apply throughout:

| Label | Meaning |
|---|---|
| **Verified repository behaviour** | Behaviour established by inspecting metadata, registry entries, executable code, policies, or models at the reviewed baseline. |
| **Source-level inference** | A potential consequence of the implementation. It has not been reproduced against a tenant. |
| **Proposed VH-003 guidance** | A validation procedure recommended for contributors and reviewers, not a claim about existing functionality. |

All repository-behaviour claims refer to the reviewed baseline unless explicitly identified as an open PR.

Source inspection establishes what the code implements. Live-tenant validation establishes whether the collection path works with actual permissions, responses, configuration and tenant scope. Record these separately.

Repository state changes. Findings should identify the reviewed commit and be rechecked when relevant collectors, policies, metadata or documentation change.

## 2. Evidence validation principles

1. **Collector declaration does not prove readiness.** A metadata reference must be checked against registration and executable implementation.
2. **Raw and derived evidence are different.** A returned record is different from a count, percentage or coverage flag calculated from it.
3. **Missing evidence establishes uncertainty.** It is not evidence of compliance or, by itself, proof of a non-compliant configuration.
4. **Configuration may require contextual review.** A configured policy or domain list may not cover the intended population or approved organizational scope.
5. **Documentation must match implementation.** Reconcile metadata, registry, collector and policy before accepting a documented evidence path.
6. **Evidence must remain traceable.** Reviewers should be able to explain how a source response becomes a policy input and stored result.

These principles guide evidence acceptance. They do not introduce new runtime statuses or override existing scan results.

## 3. Evidence provenance and traceability

Use the following path when reviewing a control:

```text
Control
→ metadata
→ registry
→ collector
→ API / PowerShell cmdlet
→ returned data
→ derived field
→ Rego policy
→ stored scan evidence
```

A broken or undocumented link weakens the conclusion. For example, a collector may return a full response, while the policy retains only a Boolean or aggregate in its `details`.

Record the following where available:

| Item | Validation purpose |
|---|---|
| Control ID and benchmark version | Identify the requirement being assessed. |
| Reviewed commit and collector ID | Establish implementation provenance. |
| API endpoint or PowerShell cmdlet | Identify the actual source operation. |
| Tenant and collection context | Establish whose configuration was observed and under what scope. |
| Collection timestamp | Support freshness assessment. |
| Raw response or protected source reference | Allow evidence to be traced or rechecked. |
| Derived field and transformation | Explain extraction, filtering, aggregation and defaults. |
| Policy input, result and retained details | Connect source evidence to the assessment. |
| Reviewer identity, date and rationale | Establish accountability when human validation is required. |

This is a proposed recording checklist. AutoAudit does not necessarily persist every item.

**Verified repository behaviour:** the worker stores policy `details` as scan evidence. It does not automatically preserve every raw collector response. The 3.1.1 policy retains the extracted audit-ingestion value; the 5.2.3.4 policy retains aggregate MFA values.

Separate uploaded-evidence records provide fields such as source filename, extracted-text hash and processing timestamp. Their existence does not prove that equivalent provenance is recorded for every automated collector.

## 4. Collector readiness verification

Before counting a control as implemented evidence coverage, verify:

- The metadata collector ID identifies the intended source.
- The collector is registered.
- Its collection method contains executable logic.
- Required authentication and source operations are available.
- The policy exists and reads the returned fields.
- Validation claims identify whether they come from inspection, tests or tenant execution.

### 4.1 Declared but unavailable: 7.2.8 and 7.2.10

**Verified repository behaviour:** both controls reference `sharepoint.spo_tenant` in metadata. The corresponding `spo_tenant.py` method raises `NotImplementedError`, and that collector ID is not registered. Both controls are `not_started` and have no policy file.

These references describe intended wiring, not an available evidence source. They must not be counted as implemented coverage simply because a collector name and Python file exist.

The worker skips non-ready controls. Their absence from automated evaluation must remain visible as a readiness limitation.

### 4.2 Conflicting validation record: 7.2.9

**Verified repository behaviour:** control 7.2.9 is marked `ready`, but its metadata note still contains a tenant-validation caveat and an instruction to change the status to ready after verification.

This is a contradiction in the recorded validation state. It does not prove that the collector fails or that later tenant testing never occurred.

**Proposed guidance:** reconcile the status with supporting validation evidence. Record what was tested, on which implementation, and which limitations remain before relying on the readiness label as evidence of validation.

## 5. Direct and derived evidence

### 5.1 MFA capability: 5.2.3.4

The MFA registration collector returns raw registration records and derives counts and a registration percentage.

The distinction matters:

- `registration_details` contains source records.
- `mfa_capable_count` counts records indicating capability.
- `mfa_registered_count` counts registration.
- `mfa_registration_percentage` represents registration, not necessarily capability.

The Rego policy checks that the population is positive and that `mfa_capable_count` equals `total_users`. A reviewer must validate the population and capability calculation, rather than substituting a registration percentage for the required condition.

### 5.2 Conditional Access flags: 5.2.2.3

**Verified repository behaviour:** the dedicated legacy-authentication collector derives `targets_all_users` from whether `includeUsers` contains `"All"`. Its returned policy representation does not carry user exclusions. The Rego policy relies on the derived flag.

**Source-level inference:** an exclusion-bearing policy can satisfy these implemented inclusion checks without establishing coverage of every relevant user. This limitation was identified in source code, not reproduced as a tenant failure.

**Proposed guidance:** validate transformations against their raw inputs. Check whether exclusions, filters or other conditions were discarded before treating a derived flag as a complete statement of coverage.

A derived value can support high confidence when its inputs, transformation and scope are verified. Derivation alone is not evidence of poor quality.

## 6. Completeness and missing-data validation

Before accepting evidence, check:

| Check | Question |
|---|---|
| Pagination | Were all available pages retrieved? |
| Population | Does the denominator represent the users or resources required by the control? |
| Empty data | Is the empty result expected, or could it reflect unavailable or incomplete collection? |
| Missing/null values | Does absence mean unknown, or is a documented default justified? |
| Filtering | Which identities or resources were omitted? |
| Exclusions | Are excluded populations visible and independently justified? |
| Source availability | Did authentication or collection prevent evidence from being obtained? |

### 6.1 Pagination example: 5.2.3.4

**Verified repository behaviour:** the Graph client defaults to a maximum of 100 pages. It returns the accumulated records when the loop ends; no truncation indicator was verified in that path.

**Source-level inference:** if another page remains after the limit, derived MFA counts describe a partial population. No actual tenant truncation was demonstrated.

**Proposed guidance:** establish whether pagination completed before accepting population-wide claims. Document any collection limit and its effect on the assessment.

### 6.2 Observed false versus unable to determine

Keep these interpretations separate:

```text
Observed false:
The relevant value was obtained and does not meet the requirement.
```

```text
Unable to determine:
The required evidence was unavailable, incomplete, missing or insufficient.
```

For example, controls 3.2.1 and 3.2.2 are `blocked`, with no configured collector or policy. Their metadata cites an IPPSSession authentication limitation. This does not establish whether a tenant has compliant DLP settings.

Some policy paths return `compliant: false` when required data cannot be determined. Review the message and evidence before describing that result as an observed configuration failure. Preserve the engine result while documenting its evidential meaning.

## 7. Automated assessment and human validation

### 7.1 Approved domains: 7.3.2

**Verified repository behaviour:** on the reviewed main baseline, the 7.3.2 collector remains a stub, metadata is `not_started`, and no policy is assigned. The implementation submitted in PR #403 is separate and was confirmed open and unmerged during this review.

The repository’s audit instructions require checking `TenantRestrictionEnabled` and `AllowedDomainList`, including whether the GUIDs correspond to trusted on-premises domains.

**Proposed guidance:** a functioning collection path can observe the restriction switch and configured list. A non-empty list does not prove that its GUIDs identify approved organizational domains. Incorrect, obsolete or unapproved identifiers can still populate a list.

For a strong conclusion, compare the configured GUIDs with independently approved on-premises domain information, such as authorized `Get-ADDomain` output. Record the comparison and reviewer rationale.

This is a proposed validation boundary, not functionality currently implemented on the reviewed main baseline. No completed domain review or live-tenant test is claimed.

### 7.2 Conditional Access review requirements

Metadata confirms **12 deferred controls** using the generic Conditional Access collector:

- **5.2.2.1, 5.2.2.4 and 5.2.2.5:** administrative-role coverage.
- **5.2.2.2:** legitimacy of exclusions.
- **1.3.2 and 5.2.2.6 through 5.2.2.12:** policy coverage.

Their collector provides configuration and derived categories, but their metadata has no policy file.

Control **5.2.2.3 is different**: it is ready and has a dedicated collector and policy. Its narrower exclusion-context limitation is described in Section 5. These are not 13 controls with an identical readiness problem.

Existing manual-verification records can associate a reviewer, comment and timestamps with a scan result. They do not establish that these contextual reviews have occurred.

## 8. Conflicting or stale documentation

Control 3.1.1 provides a confirmed example.

On the reviewed baseline:

- `controls.md` names `exchange.organization.organization_config` and `AuditDisabled = False`.
- Metadata names `exchange.organization.admin_audit_log_config`.
- The Rego policy reads `unified_audit_log_ingestion_enabled` and requires `true`.
- `admin_audit_log_config.py` explicitly supports 3.1.1.
- `organization_config.py` associates `AuditDisabled` with 6.1.1 and does not list 3.1.1.

PR #405 was submitted separately to correct the documentation and was confirmed open and unmerged during this review.

**Validation rule:** where documentation and executable implementation conflict, reconcile metadata, registry, collector implementation and policy before accepting the documented evidence path. Record the mismatch and correction reference. Do not silently treat either documentation or code as sufficient proof without checking the chain.

## 9. Proposed evidence-confidence model

The following levels supplement VH-001 evidence classification. They are **VH-003 guidance**, not AutoAudit engine fields, runtime statuses or replacements for policy results.

| Confidence | Criteria |
|---|---|
| **High** | Source is known; collector is executable; evidence is complete; transformations are traceable; policy evaluates the required condition; no unresolved contextual dependency remains. |
| **Medium** | Evidence is available and traceable, but derived values still require validation, completeness is unverified, or contextual review remains outstanding. |
| **Low** | Collector is unavailable or stubbed; evidence is known to be incomplete; provenance is unclear; documentation conflicts remain unresolved; or a critical validation dependency prevents a defensible conclusion. |

Record the reason for the level. Medium confidence must not conceal a known material gap. A critical unresolved dependency warrants low confidence.

Confidence concerns the strength of the evidence. High-confidence evidence may establish non-compliance. A passing policy result does not automatically imply high confidence.

## 10. Contributor validation checklist

Before proposing that a control be marked ready:

- [ ] Control ID and benchmark version are correct.
- [ ] Metadata points to the intended collector.
- [ ] The collector is registered and executable.
- [ ] The API or cmdlet matches the required evidence.
- [ ] Raw evidence and collection context are understood.
- [ ] Derived fields are traceable to inputs and transformations.
- [ ] Pagination, population and completeness have been checked.
- [ ] Empty, missing and null values have defined interpretations.
- [ ] Exclusions and filtering scope have been reviewed.
- [ ] Rego wiring exists and reads the intended fields.
- [ ] Documentation matches metadata and implementation.
- [ ] Human-review dependencies are recorded.
- [ ] Validation limitations and the reviewed commit are documented.
- [ ] Source inspection, automated tests and live-tenant validation are distinguished.

An unresolved item should be recorded and reviewed, not converted into an unsupported readiness claim.

## 11. Escalation and existing status handling

Escalate evidence for review when a collector is missing, results are incomplete, sources conflict, exclusions lack explanation, domain ownership needs independent confirmation, documentation disagrees with implementation, or the validation record is stale.

Record the affected control, source references, limitation, required reviewer and evidence needed to resolve it. Revalidate after relevant changes.

Preserve existing project statuses:

- Metadata: `ready`, `deferred`, `blocked`, `manual`, `not_started`.
- Scan results: `pending`, `passed`, `failed`, `error`, `skipped`.

The automated worker dispatches ready controls and records non-ready controls as skipped. Where collection and policy evaluation complete successfully, the compliance result can be passed or failed; collection or evaluation problems remain distinguishable through error outcomes, while skipped outcomes identify controls not evaluated.

Manual-verification records exist, but the inspected path does not implement a combined “compliant with review” outcome.

VH-003 does not introduce `compliant_with_review` or any other runtime status. Record unresolved validation needs using existing review mechanisms and supporting documentation.

## 12. Reference cases

| Control | Validation issue | Evidence quality lesson | Required action |
|---|---|---|---|
| 7.2.8 / 7.2.10 | Declared collector is stubbed and unregistered. | Metadata is not implemented coverage. | Verify execution and wiring before claiming availability. |
| 7.3.2 | Domain configuration needs independent organizational validation; main remains a stub. | Non-empty does not mean approved or correct. | Separate intended collection from domain-ownership review. |
| 5.2.2.3 | Derived coverage omits exclusion context. | A flag may lose material scope information. | Review raw conditions and exclusions; retain the source-level caveat. |
| 12 deferred CA controls | Contextual coverage remains unresolved. | Configuration collection is not complete compliance assessment. | Record role, exclusion and coverage review requirements. |
| 3.1.1 | Documentation conflicts with implemented evidence wiring. | Traceability requires reconciliation. | Track the documentation correction separately. |
| 5.2.3.4 | Aggregate validity depends on population and pagination. | Complete-looking counts can describe partial evidence. | Check collection completion and denominators. |
| 7.2.9 | Ready status conflicts with a validation caveat. | Readiness needs a consistent supporting record. | Reconcile the caveat with validation evidence. |
| 3.2.1 / 3.2.2 | Sources are blocked and unwired. | Unavailable evidence does not establish tenant configuration. | Preserve the limitation and identify the collection dependency. |

## 13. Reviewed repository references

These paths support the examples at the reviewed main baseline:

**Control metadata, policies and documentation**

- `engine/policies/cis/microsoft-365-foundations/v6.0.0/metadata.json`
- `engine/policies/cis/microsoft-365-foundations/v6.0.0/`, particularly the 3.1.1, 5.2.2.3, 5.2.3.4 and 7.2.9 Rego policies
- `docs/engine/policies/cis/microsoft-365-foundations/v6.0.0/controls.md`
- `docs/engine/Framework/CIS_M365_Benchmarks.json`

**Collector wiring, source operations and transformations**

- `engine/collectors/registry.py`
- `engine/collectors/graph_client.py`
- `engine/collectors/sharepoint/spo_tenant.py`
- `engine/collectors/sharepoint/spo_sync_client_restriction.py`
- `engine/collectors/sharepoint/pnp/tenant.py`
- `engine/collectors/entra/conditional_access/conditional_access_policies.py`
- `engine/collectors/entra/conditional_access/legacy_auth_block.py`
- `engine/collectors/entra/authentication/mfa_registration_report.py`
- `engine/collectors/exchange/organization/organization_config.py`
- `engine/collectors/exchange/organization/admin_audit_log_config.py`

**Evaluation, evidence retention and manual verification**

- `engine/worker/tasks.py`
- `backend-api/app/models/scan_result.py`
- `backend-api/app/models/evidence_validation.py`
- `backend-api/app/models/manual_scan_result_detail.py`
- `backend-api/app/api/v1/manual_verification.py`

**Separate PR references**

- PR #403: proposed 7.3.2 implementation, open/unmerged at review time.
- PR #405: proposed 3.1.1 documentation correction, open/unmerged at review time.
