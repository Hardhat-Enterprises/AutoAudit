# Audit Readiness Summary

The benchmark Audit Readiness Summary endpoint gives the frontend and project team a quick view of how much of a benchmark is currently ready to be audited.

## Endpoint

`GET /v1/benchmarks/{framework}/{slug}/{version}/audit-readiness`

Authentication is required, consistent with the existing benchmark endpoints.

## How readiness is calculated

Controls with `automation_status` equal to `ready` or `manual` are counted as audit-ready:

- `ready` means the automated collector/policy path is available.
- `manual` means the benchmark explicitly requires manual verification, so the control can still be completed as part of an audit.

The following statuses are treated as readiness gaps:

- `deferred`
- `blocked`
- `not_started`
- any unknown status

The readiness percentage is:

`audit_ready_controls / total_controls * 100`

An empty benchmark returns `0.0` percent and an `empty` status rather than raising a division error.

## Response

The response includes:

- benchmark identity (`framework`, `slug`, `version`, `benchmark`)
- total and audit-ready control counts
- counts for ready, manual, deferred, blocked, not-started, and unknown controls
- readiness percentage
- overall status (`ready`, `needs_attention`, or `empty`)
- a `gaps` list containing controls that still need attention

Gap entries include the control ID, title, automation status, severity, service, required permissions, and notes when available.

## Purpose

This endpoint is different from pre-scan connection readiness. Pre-scan readiness checks whether a selected Microsoft 365 connection and permissions look runnable before a scan. Benchmark audit readiness instead summarises implementation coverage from control metadata so the team can see which benchmark controls are ready and which still need engineering or manual attention.
