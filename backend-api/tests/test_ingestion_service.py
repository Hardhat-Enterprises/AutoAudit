"""Tests for the ingestion service module."""

import pytest
from app.ingestion_service import IngestionService


def test_ingestion_service_basic():
    """Test that the ingestion service initializes and processes sample data."""
    service = IngestionService()
    result = service.process_sample_data()
    assert result is not None  # nosec B101
