# 26T3-DEV-BH-002: Verify Grype blocks Critical vulnerabilities on PRs

**Owner:** Ben Holloway | **Date:** 20 Nov 2026 | **Status:** Complete (verification), with open items (see section 6)
**Verifying:** PR #326 (Grype fails CI on Critical-severity findings), workflow `.github/workflows/ci.grype.yml`

---

## 1. TL;DR

- **Detection works.** Grype turns the check red when Critical vulnerabilities exist. Seen in real CI runs and reproduced locally.
- **`main` is not clean.** It currently fails the same check: 19 Critical findings, nearly all fixable by version bumps.
- **So "clean PR passes" cannot currently be shown.** Any PR touching `frontend/`, `backend-api/` or `engine/` inherits `main`'s Criticals and fails regardless of what the PR changes.
- **Red probably does not block merging.** On PR #439 the failing Grype check has no "Required" label (only review rules are shown). Admin confirmation still needed.
- **GitHub already computes a diff.** On the same PR, `Code scanning results / grype` reports "No new alerts in code changed by this pull request" while the scan check is red. This is direct evidence for a diff gate, and may make it mostly a settings change.
- **Consequence:** this supports a diff-style gate (fail only on findings a PR introduces), which becomes its own card and decides 003.

## 2. What the card asked for

> A test PR in a fork with a known-Critical dependency fails CI, and a clean PR passes. Screenshots and notes attached. We are VERIFYING that PR #326 actually works.

## 3. What the workflow does (read from `ci.grype.yml`)

| Item | Behaviour |
|---|---|
| Triggers | Push to `main`, PRs into `main`, weekly schedule (Thursdays) |
| Path filter | Push and PR triggers only fire if `frontend/**`, `backend-api/**` or `engine/**` changed. PRs touching only docs or `.github` skip the check (a skip looks like a pass). |
| Scan type | Directory scan of the whole repo (`path: "."`), not an image scan. Reads dependency manifests and lockfiles. |
| Gate | `fail-build: true`, `severity-cutoff: critical` (CI runs `grype ... --fail-on critical dir:.`) |
| Unfixed vulns | No `--only-fixed` flag, so Criticals with no fix also fail the build |
| Report | SARIF uploaded to the Security tab on every run (`if: always()`) |
| Grype version in CI | v0.97.1 |

## 4. What we did

1. Checked the local clone: remotes (`origin` = Hardhat-Enterprises, `fork` = Hexlow-0), clean working tree, synced local `main` to `origin/main` (9c22b0ce), then pushed it to the fork.
2. Read `ci.grype.yml` (section 3).
3. Reviewed recent upstream Grype runs on the Actions tab, including the `main` push run.
4. Read the step logs of failing runs #666 and #667.
5. Installed Grype v0.97.1 locally (same version as CI) and scanned `main` with `grype dir:. --fail-on critical`.

## 5. Evidence

### 5.1 CI runs

| Run | Trigger | Result | Notes |
|---|---|---|---|
| #661 | Push to `main` (merge of PR #435, commit 9c22b0c) | Failed | `main` itself fails the gate |
| #664, #665, #667 | PR #439 (tim025-star) | Failed | Engine PR |
| #666 | PR #440 (steph-marcy) | Failed | Engine PR, different author |

Log findings (#666, #667):
- Scan step error: "Failed minimum severity level. Found vulnerabilities with level 'critical' or higher".
- The vulnerability table is **not** in the log (output is SARIF), so details live in the Security tab or a local scan.
- In #666 the SARIF upload step validated and uploaded successfully, so the failures come from real findings, not from the upload step.
- Warnings only: Node.js 20 deprecation, and CodeQL Action v3 deprecated December 2026 (upgrade to v4).

### 5.2 Local reproduction (Grype v0.97.1, `main` at 9c22b0ce)

- Packages cataloged: 450
- Vulnerability matches: 252 (250 fixed, 2 not-fixed, 0 ignored)
- By severity: **19 critical**, 119 high, 102 medium, 12 low, 0 negligible
- Exit code: 2 (matches CI)

### 5.3 Critical findings by package (from pasted output)

| Package | Version(s) found | Fixed in | Notes |
|---|---|---|---|
| pillow | 12.2.0 | 13.0.0 (one issue: 12.3.0) | Most rows; each flaw appears as a CVE and a GHSA alias |
| cryptography | 46.0.3 | 46.0.7 | Relevant to token encryption; reachability not assessed |
| anyio | 4.10.0, 4.12.0 | 4.14.2 | Two versions, so likely two manifests or lockfiles |
| pyjwt | 2.10.1, 2.12.1 | 2.14.0 | Relevant to JWT signing; reachability not assessed |
| certifi | 2025.11.12 | 2026.10.18 | |

Note: the pasted table showed 18 rows against 19 in the summary. The JSON output will give an exact count.

## 6. Not verified / open items

- **Does red block merging?** PR #439's merge box shows review requirements but no "Required" label on the failing Grype check (3 failing, 1 neutral, 17 successful). Likely advisory, but not confirmed from Settings > Rules/Branches. Needs a repo admin.
- **Engine CI/CD #376** also failed on the same `main` push. Cause not yet investigated. (On #439, the Engine failure is Prettier JSON formatting, unrelated to Grype.)
- **`Code scanning results / CodeQL` is neutral: "1 configuration not found".** Possible misconfiguration, out of scope for 002.
- **Local scan may include untracked files** (`node_modules`, `.venv`), so 450 packages could be higher than what CI sees.
- **Reachability** of the cryptography and pyjwt findings is unassessed. A version match is not proof of exploitability.
- **Deliberately vulnerable test PR in the fork was not run.** The existing runs already show the gate firing, and a red fork PR would not be distinguishable from the baseline failure.

## 7. Outcome against the card's criteria

| Criterion | Result |
|---|---|
| Known-Critical PR fails CI | Demonstrated by existing runs (#664 to #667) and local reproduction, not by a purpose-built test PR |
| Clean PR passes | Cannot be shown: `main` already has 19 Criticals, so no PR in the watched paths can pass |
| Screenshots and notes | This document, plus run screenshots and the saved scan output |

**Conclusion:** PR #326 works as a detector. Its value as a gate depends on the merge-blocking check, and on the baseline problem below.

## 8. What this means for the diff-gate card

- A whole-repo gate fails PRs for findings they did not introduce, which blocks or desensitises contributors.
- A diff gate (fail only on findings new relative to base) fixes that, but hides old vulnerabilities forever unless paired with a **scheduled full scan** reporting the whole backlog.
- **Evidence from PR #439:** the Grype scan check is red, yet `Code scanning results / grype` says no new alerts in code changed by the PR. GitHub code scanning already does the base-vs-PR comparison from the uploaded SARIF. A first option to test is making that check (or a code-scanning ruleset with a severity threshold) the gate, instead of building a custom diff. Confirm what rulesets allow and what an admin can configure.
- The vulnerability database updates daily. A diff must compare base and PR using the **same database at the same time**, or it reports false differences.
- Fixing the existing Criticals means editing dependency files owned by other teams. Route via GitHub issue, linked Planner card, and team-lead ping.
- The answer to 003 (block on High?) depends on this: blanket High blocking is wrong on the current gate, but blocking on *new* High findings may be reasonable with a diff gate.

## 9. Proposed discussion points for the call

1. Agree the diff gate is its own card, owned by Ben and Steven, with a timebox of a day or two (otherwise a design note and Sprint 2).
2. Check Grype's built-in options (ignore file with justifications) before building anything custom.
3. Decide the scheduled full-scan report as the compensating control.
4. Agree how the existing Criticals get handed to owning teams.
5. Close 003 afterwards with one decision note.

## 10. Evidence checklist

- [ ] Screenshot: Actions list filtered to `main` showing #661 red
- [ ] Screenshot: #666 or #667 failing scan step
- [ ] Screenshot: PR #439 merge box (Required or not)
- [ ] Saved local scan output (`~/grype-main-baseline.txt`, `.json`), not committed
- [ ] Link this document and the PR and run numbers on the Planner card

## 11. Outcome of the DevSecOps call (20 Nov 2026)

Attendees: Ben Holloway, Steven Duzevich.

- **002:** closed as verification. Detection confirmed; blocking not confirmed (advisory, pending admin check).
- **High severity:** do not block. Keep it an easy switch (a Grype flag) and document it. Project lead agreed with the direction; the project mentor confirmed the decision sits with the project group, so no further sign-off is needed. Card 003 to close with a decision note.
- **Diff gate:** new card, owned by Ben and Steven, timeboxed to a day or two. First experiment: a PR in a fork that adds a vulnerable dependency, to confirm the diff-based check flags something new. If the built-in code scanning check is close enough, use it; a custom diff in the workflow may be a bigger job than expected, in which case write a design note and move to Sprint 2.
- **Policy question raised:** block on fixable Criticals and never allow them to be allowlisted? Open design question for the new card, including whether unfixable Criticals are treated differently.
- **Ideas logged:** upload the Grype report as a build artifact (single `upload-artifact` step); evaluate an additional code scanning tool for Sprint 2 (possible overlap with Gitleaks); ask other teams what in the workflows they are unhappy with.
- **Handoff:** the 19 Critical findings go to the owning teams to bump (existing issue #432), via the agreed issue, Planner card and team-chat process.
