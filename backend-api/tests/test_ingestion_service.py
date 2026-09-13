"""Unit tests for backend security ingestion service."""

import os
import tempfile
from typing import Generator

import pytest

from app.ingestion_service import (
    check_file_size,
    generate_file_hash,
    process_ingestion_security_pipeline,
    validate_file_extension,
)


@pytest.fixture
def temp_test_file() -> Generator[str, None, None]:
    """Create a temporary valid text file for testing."""
    with tempfile.NamedTemporaryFile(
        suffix=".txt", delete=False
    ) as temp_file:  # nosec B108 - safe tempfile creation for test runner
        temp_file.write(b"AutoAudit Test Content")
        temp_path = temp_file.name
    yield temp_path
    if os.path.exists(temp_path):
        os.remove(temp_path)


def test_validate_file_extension_allowed(temp_test_file: str) -> None:
    """Verify that permitted file extensions pass validation."""
    assert validate_file_extension(temp_test_file) is True  # nosec B101 - pytest assertion


def test_validate_file_extension_disallowed() -> None:
    """Verify that disallowed file extensions fail validation."""
    assert validate_file_extension("malicious_script.exe") is False  # nosec B101 - pytest assertion


def test_check_file_size_within_limit(temp_test_file: str) -> None:
    """Verify that files within size limit pass check_file_size."""
    assert check_file_size(temp_test_file, max_size_mb=1.0) is True  # nosec B101 - pytest assertion


def test_check_file_size_exceeding_limit(temp_test_file: str) -> None:
    """Verify that files exceeding size limit fail check_file_size."""
    assert check_file_size(temp_test_file, max_size_mb=0.000001) is False  # nosec B101 - pytest assertion


def test_missing_file() -> None:
    """Verify pipeline gracefully handles non-existent file path."""
    success, hash_val, msg = process_ingestion_security_pipeline(
        "non_existent_file.pdf"
    )
    assert success is False  # nosec B101 - pytest assertion
    assert hash_val is None  # nosec B101 - pytest assertion
    assert "File not found" in msg  # nosec B101 - pytest assertion


def test_successful_pipeline_execution(temp_test_file: str) -> None:
    """Verify end-to-end pipeline execution for valid input file."""
    success, hash_val, msg = process_ingestion_security_pipeline(temp_test_file)
    assert success is True  # nosec B101 - pytest assertion
    assert hash_val is not None  # nosec B101 - pytest assertion
    assert len(hash_val) == 64  # nosec B101 - pytest assertion
    assert "successfully validated" in msg  # nosec B101 - pytest assertion


def test_hash_generation(temp_test_file: str) -> None:
    """Verify SHA-256 hash generation output format and length."""
    digest = generate_file_hash(temp_test_file)
    assert digest is not None  # nosec B101 - pytest assertion
    assert isinstance(digest, str)  # nosec B101 - pytest assertion
    assert len(digest) == 64  # nosec B101 - pytest assertion
