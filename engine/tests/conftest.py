"""Pytest configuration for engine tests.

Writes a clean markdown summary to GitHub Actions job summary
so PR reviewers can see exactly what failed without reading logs.
"""

from __future__ import annotations

import os
import re
from collections import defaultdict

import pytest

# Friendly names for each test function
_TEST_LABELS = {
    "test_ready_control_policy_file_exists": "Missing policy file",
    "test_ready_control_collector_registered": "Unregistered collector",
    "test_rego_package_matches_metadata": "Rego package mismatch",
    "test_no_orphaned_rego_files": "Orphaned rego file",
    "test_no_orphaned_collectors": "Orphaned collector",
    "test_control_schema_consistency": "Schema inconsistency",
    "test_no_duplicate_control_ids": "Duplicate control ID",
}

_failures: list[tuple[str, str]] = []


def _extract_message(report: pytest.TestReport) -> str:
    """Pull the assertion message out of the report."""
    text = report.longreprtext
    # Look for the line after "AssertionError:" or "AssertionError: "
    match = re.search(r"AssertionError:\s*(.+?)(?:\n|$)", text)
    if match:
        return match.group(1).strip()
    # Fallback: last non-empty line
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    return lines[-1] if lines else "Unknown failure"


def pytest_runtest_logreport(report: pytest.TestReport) -> None:
    if report.when == "call" and report.failed:
        func_name = report.nodeid.split("::")[-1].split("[")[0]
        label = _TEST_LABELS.get(func_name, func_name)
        message = _extract_message(report)
        _failures.append((label, message))


def pytest_terminal_summary(
    terminalreporter: pytest.TerminalReporter,
    exitstatus: int,
    config: pytest.Config,
) -> None:
    summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
    if not summary_path:
        return

    passed = len(terminalreporter.stats.get("passed", []))
    xfailed = len(terminalreporter.stats.get("xfailed", []))
    failed = len(_failures)

    with open(summary_path, "a", encoding="utf-8") as f:
        if not _failures:
            f.write("## Engine Structural Checks Passed\n\n")
            f.write(f"**{passed}** checks passed")
            if xfailed:
                f.write(f", **{xfailed}** expected failures")
            f.write("\n")
            return

        f.write("## Engine Structural Checks Failed\n\n")
        f.write(f"**{failed}** failed, **{passed}** passed")
        if xfailed:
            f.write(f", **{xfailed}** expected failures")
        f.write("\n\n")

        # Group failures by category
        grouped: dict[str, list[str]] = defaultdict(list)
        for label, message in _failures:
            grouped[label].append(message)

        for label, messages in grouped.items():
            f.write(f"### {label}\n\n")
            for msg in messages:
                f.write(f"- {msg}\n")
            f.write("\n")
