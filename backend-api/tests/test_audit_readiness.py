"""Unit tests for benchmark-level audit readiness calculations."""

import unittest

from app.services.audit_readiness import (
    list_audit_readiness_gaps,
    summarise_audit_readiness,
)


class AuditReadinessSummaryTests(unittest.TestCase):
    """Verify readiness counts, percentage, status, and gap details."""

    def test_mixed_controls_are_summarised_correctly(self):
        controls = [
            {"control_id": "1", "automation_status": "ready"},
            {"control_id": "2", "automation_status": "manual"},
            {"control_id": "3", "automation_status": "blocked"},
            {"control_id": "4", "automation_status": "not_started"},
        ]

        summary = summarise_audit_readiness(controls)

        self.assertEqual(summary["total_controls"], 4)
        self.assertEqual(summary["audit_ready_controls"], 2)
        self.assertEqual(summary["gap_controls"], 2)
        self.assertEqual(summary["ready_controls"], 1)
        self.assertEqual(summary["manual_controls"], 1)
        self.assertEqual(summary["blocked_controls"], 1)
        self.assertEqual(summary["not_started_controls"], 1)
        self.assertEqual(summary["readiness_percentage"], 50.0)
        self.assertEqual(summary["status"], "needs_attention")

    def test_all_ready_and_manual_controls_return_ready_status(self):
        controls = [
            {"automation_status": "ready"},
            {"automation_status": "manual"},
            {"automation_status": "READY"},
        ]

        summary = summarise_audit_readiness(controls)

        self.assertEqual(summary["audit_ready_controls"], 3)
        self.assertEqual(summary["gap_controls"], 0)
        self.assertEqual(summary["readiness_percentage"], 100.0)
        self.assertEqual(summary["status"], "ready")

    def test_empty_benchmark_is_reported_without_division_error(self):
        summary = summarise_audit_readiness([])

        self.assertEqual(summary["total_controls"], 0)
        self.assertEqual(summary["readiness_percentage"], 0.0)
        self.assertEqual(summary["status"], "empty")

    def test_unknown_and_missing_statuses_are_readiness_gaps(self):
        controls = [
            {
                "control_id": "1.1",
                "title": "Missing status",
                "severity": "medium",
            },
            {
                "control_id": "1.2",
                "title": "Unexpected status",
                "automation_status": "experimental",
                "requires_permissions": ["User.Read.All"],
            },
        ]

        summary = summarise_audit_readiness(controls)
        gaps = list_audit_readiness_gaps(controls)

        self.assertEqual(summary["not_started_controls"], 1)
        self.assertEqual(summary["unknown_controls"], 1)
        self.assertEqual(summary["gap_controls"], 2)
        self.assertEqual(len(gaps), 2)
        self.assertEqual(gaps[0]["automation_status"], "not_started")
        self.assertEqual(gaps[1]["automation_status"], "experimental")
        self.assertEqual(gaps[1]["requires_permissions"], ["User.Read.All"])


if __name__ == "__main__":
    unittest.main()
