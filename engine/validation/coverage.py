from dataclasses import dataclass

from validation.discovery import ControlDefinition


ControlKey = tuple[str, str, str, str]


@dataclass
class CoverageSummary:
    ready_controls: int
    tested_controls: int
    coverage_percent: float


def calculate_behavioral_coverage(
    controls: dict[ControlKey, ControlDefinition],
    tested_control_keys: set[ControlKey],
) -> CoverageSummary:
    """
    Calculate behavioural verification coverage for ready,
    automated policy-backed controls.
    """

    ready_control_keys = {
        key
        for key, control in controls.items()
        if (
            (control.automation_status or "").lower() == "ready"
            and
            (control.benchmark_audit_type or "").lower() == "automated"
        )
    }

    tested_ready_controls = ready_control_keys & tested_control_keys

    ready_count = len(ready_control_keys)
    tested_count = len(tested_ready_controls)

    coverage_percent = (
        (tested_count / ready_count) * 100
        if ready_count > 0
        else 0.0
    )

    return CoverageSummary(
        ready_controls=ready_count,
        tested_controls=tested_count,
        coverage_percent=coverage_percent,
    )