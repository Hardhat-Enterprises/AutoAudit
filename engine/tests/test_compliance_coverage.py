"""Tests for behavioural coverage calculation."""

# pylint: disable=missing-function-docstring
from pathlib import Path

import pytest

from validation.coverage import calculate_behavioral_coverage
from validation.discovery import ControlDefinition


def make_control(
    control_id: str,
    automation_status: str = "ready",
    benchmark_audit_type: str = "Automated",
) -> ControlDefinition:
    return ControlDefinition(
        framework="cis",
        benchmark="microsoft-365-foundations",
        version="v6.0.0",
        control_id=control_id,
        policy_path=Path(f"{control_id}.rego"),
        package=f"test.control_{control_id.replace('.', '_')}",
        query=f"data.test.control_{control_id.replace('.', '_')}.result",
        metadata_path=Path("metadata.json"),
        automation_status=automation_status,
        benchmark_audit_type=benchmark_audit_type,
    )


def test_coverage_counts_ready_automated_controls():
    controls = {
        ("cis", "microsoft-365-foundations", "v6.0.0", "1.1.1"):
            make_control("1.1.1"),
        ("cis", "microsoft-365-foundations", "v6.0.0", "1.1.2"):
            make_control("1.1.2"),
        ("cis", "microsoft-365-foundations", "v6.0.0", "1.1.3"):
            make_control("1.1.3"),
    }

    tested = {
        ("cis", "microsoft-365-foundations", "v6.0.0", "1.1.1"),
    }

    summary = calculate_behavioral_coverage(controls, tested)

    assert summary.ready_controls == 3
    assert summary.tested_controls == 1
    assert summary.coverage_percent == pytest.approx(33.333, rel=0.01)


def test_non_ready_controls_are_excluded():
    controls = {
        ("cis", "microsoft-365-foundations", "v6.0.0", "1.1.1"):
            make_control("1.1.1", automation_status="ready"),
        ("cis", "microsoft-365-foundations", "v6.0.0", "1.1.2"):
            make_control("1.1.2", automation_status="in-progress"),
    }

    tested = {
        ("cis", "microsoft-365-foundations", "v6.0.0", "1.1.1"),
        ("cis", "microsoft-365-foundations", "v6.0.0", "1.1.2"),
    }

    summary = calculate_behavioral_coverage(controls, tested)

    assert summary.ready_controls == 1
    assert summary.tested_controls == 1
    assert summary.coverage_percent == 100.0


def test_manual_controls_are_excluded():
    controls = {
        ("cis", "microsoft-365-foundations", "v6.0.0", "1.1.1"):
            make_control("1.1.1", benchmark_audit_type="Automated"),
        ("cis", "microsoft-365-foundations", "v6.0.0", "1.1.2"):
            make_control("1.1.2", benchmark_audit_type="Manual"),
    }

    tested = {
        ("cis", "microsoft-365-foundations", "v6.0.0", "1.1.1"),
        ("cis", "microsoft-365-foundations", "v6.0.0", "1.1.2"),
    }

    summary = calculate_behavioral_coverage(controls, tested)

    assert summary.ready_controls == 1
    assert summary.tested_controls == 1
    assert summary.coverage_percent == 100.0


def test_untested_ready_controls_reduce_coverage():
    controls = {
        ("cis", "microsoft-365-foundations", "v6.0.0", "1.1.1"):
            make_control("1.1.1"),
        ("cis", "microsoft-365-foundations", "v6.0.0", "1.1.2"):
            make_control("1.1.2"),
    }

    tested = set()

    summary = calculate_behavioral_coverage(controls, tested)

    assert summary.ready_controls == 2
    assert summary.tested_controls == 0
    assert summary.coverage_percent == 0.0


def test_zero_ready_controls_returns_zero_percent():
    controls = {
        ("cis", "microsoft-365-foundations", "v6.0.0", "1.1.1"):
            make_control(
                "1.1.1",
                automation_status="in-progress",
            )
    }

    tested = set()

    summary = calculate_behavioral_coverage(controls, tested)

    assert summary.ready_controls == 0
    assert summary.tested_controls == 0
    assert summary.coverage_percent == 0.0
