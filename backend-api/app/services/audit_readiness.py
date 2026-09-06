"""Calculate benchmark-level audit readiness from control metadata."""

from __future__ import annotations

from typing import Any

AUDIT_READY_STATUSES = {"ready", "manual"}
KNOWN_AUTOMATION_STATUSES = {
    "ready",
    "manual",
    "deferred",
    "blocked",
    "not_started",
}


def _normalise_status(control: dict[str, Any]) -> str:
    """Return a normalised automation status for a control."""
    status = control.get("automation_status", "not_started")
    if not isinstance(status, str) or not status.strip():
        return "not_started"
    return status.strip().lower()


def summarise_audit_readiness(controls: list[dict[str, Any]]) -> dict[str, Any]:
    """Summarise how many benchmark controls are currently audit-ready.

    A control is considered audit-ready when its automation status is either
    ``ready`` (the automated collector/policy path is available) or ``manual``
    (the benchmark explicitly requires manual verification). Deferred,
    blocked, not-started, and unknown statuses are treated as readiness gaps.
    """
    counts = {
        "ready": 0,
        "manual": 0,
        "deferred": 0,
        "blocked": 0,
        "not_started": 0,
        "unknown": 0,
    }

    for control in controls:
        status = _normalise_status(control)
        if status in KNOWN_AUTOMATION_STATUSES:
            counts[status] += 1
        else:
            counts["unknown"] += 1

    total_controls = len(controls)
    audit_ready_controls = counts["ready"] + counts["manual"]
    gap_controls = total_controls - audit_ready_controls
    readiness_percentage = (
        round((audit_ready_controls / total_controls) * 100, 1)
        if total_controls
        else 0.0
    )

    if total_controls == 0:
        readiness_status = "empty"
    elif gap_controls == 0:
        readiness_status = "ready"
    else:
        readiness_status = "needs_attention"

    return {
        "total_controls": total_controls,
        "audit_ready_controls": audit_ready_controls,
        "gap_controls": gap_controls,
        "ready_controls": counts["ready"],
        "manual_controls": counts["manual"],
        "deferred_controls": counts["deferred"],
        "blocked_controls": counts["blocked"],
        "not_started_controls": counts["not_started"],
        "unknown_controls": counts["unknown"],
        "readiness_percentage": readiness_percentage,
        "status": readiness_status,
    }


def list_audit_readiness_gaps(
    controls: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Return controls that still need work before the benchmark is audit-ready."""
    gaps: list[dict[str, Any]] = []

    for control in controls:
        automation_status = _normalise_status(control)
        if automation_status in AUDIT_READY_STATUSES:
            continue

        gaps.append(
            {
                "control_id": control.get("control_id", ""),
                "title": control.get("title", ""),
                "automation_status": automation_status,
                "severity": control.get("severity"),
                "service": control.get("service"),
                "requires_permissions": control.get("requires_permissions"),
                "notes": control.get("notes"),
            }
        )

    return gaps
