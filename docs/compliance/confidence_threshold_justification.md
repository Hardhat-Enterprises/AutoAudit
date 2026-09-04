# Confidence Scoring Threshold Justification

## What this document is

When an auditor uploads a screenshot or document as evidence for a
manual control, AutoAudit extracts the text from that file and checks
how many of the control's keywords appear in it. That gives a match
percentage. This document explains how that percentage gets turned
into a suggestion — pass, review, or fail — and why the bar is set
differently depending on how serious the control is.

## The basic thresholds

| Match percentage | Suggestion | What it means |
|---|---|---|
| >= 80% | Suggest pass | Enough keywords found — the right settings page was probably captured |
| 50–79% | Flag for review | Some keywords matched but not enough to be confident — auditor should take another look |
| < 50% | Suggest fail | Too few keywords found — the evidence does not clearly show compliance |

These are starting values. The algorithm adjusts them up or down
based on how serious the control is.

## Why severity changes the bar

Not every control carries the same risk if it gets marked wrong.

Getting a high severity control wrong in the pass direction — telling
an auditor the tenant is compliant when it is not — can have serious
real-world consequences. So the algorithm demands more keyword matches
before it suggests pass on those controls.

Getting a low severity control wrong in the fail direction — flagging
something as non-compliant when it actually is fine — just creates
unnecessary work for the auditor. That is a much smaller problem, so
the bar can be a little lower.

**A concrete example on the high end — control 1.1.2:**
This control checks that two emergency access accounts exist. If the
scoring algorithm incorrectly marks this as passed when no break-glass
accounts are set up, the tenant has no fallback if all primary admin
accounts get locked out. That is a genuine security crisis. The
algorithm requiring a higher keyword match percentage before suggesting
pass is the right call.

**A concrete example on the low end — control 5.1.2.5:**
This control checks whether the stay signed in option is hidden on
the login page. If the algorithm incorrectly flags this as failed, an
admin spends five minutes double-checking a low-risk setting. That is
the entire cost of getting it wrong. A lower threshold here is fine.

## Connection to the AutoAudit Risk Matrix

This approach comes directly from the risk thinking already documented
in the AutoAudit Risk-Impact Prioritisation Matrix. R-06 in that
matrix covers unauthenticated FastAPI endpoints — a gap that looked
minor but was actually exploitable. The lesson from R-06 is that
assuming something is compliant without proper verification is where
real security problems start.

Tighter thresholds on high and critical controls exist for exactly
that reason. The algorithm should be conservative when the cost of
being wrong is high.

## Thresholds per severity level

| Severity | Suggest pass | Flag for review | Suggest fail |
|---|---|---|---|
| Critical | >= 90% | 60–89% | < 60% |
| High | >= 80% | 50–79% | < 50% |
| Medium | >= 70% | 40–69% | < 40% |
| Low | >= 60% | 30–59% | < 30% |

These values are implemented in
`backend-api/app/services/confidence_scorer.py` in the
`PASS_THRESHOLDS` and `REVIEW_THRESHOLDS` dictionaries. If the team
decides to adjust any of these values after testing, update both this
document and the code at the same time so they stay in sync.