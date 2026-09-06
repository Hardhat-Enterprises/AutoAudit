"""Tests for the AutoAudit readiness endpoint."""

import unittest
from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from app.main import app


class ReadinessEndpointTests(unittest.TestCase):
    """Tests for the database readiness endpoint."""

    def setUp(self):
        self.client = TestClient(app)

    @patch("app.main.database_ready", new_callable=AsyncMock)
    def test_readiness_returns_200_when_database_available(
        self,
        mock_database_ready,
    ):
        """Readiness should return 200 when the database is available."""
        mock_database_ready.return_value = True

        response = self.client.get("/readiness")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                "status": "ready",
                "checks": {
                    "database": "ok",
                },
            },
        )

    @patch("app.main.database_ready", new_callable=AsyncMock)
    def test_readiness_returns_503_when_database_unavailable(
        self,
        mock_database_ready,
    ):
        """Readiness should return 503 when the database is unavailable."""
        mock_database_ready.return_value = False

        response = self.client.get("/readiness")

        self.assertEqual(response.status_code, 503)
        self.assertEqual(
            response.json(),
            {
                "status": "not_ready",
                "checks": {
                    "database": "unavailable",
                },
            },
        )


if __name__ == "__main__":
    unittest.main()