"""Tests for the ingestion service module."""

import os
import tempfile
import pytest

# pylint: disable=wrong-import-position
from app.ingestion_service import (
    check_file_size,
    generate_file_hash,
    process_ingestion_security_pipeline,
    validate_file_extension,
)
# pylint: enable=wrong-import-position


def test_validate_file_extension_valid():
    """Test valid file extensions pass validation."""
    assert validate_file_extension("document.pdf") is True  # nosec B101
    assert validate_file_extension("report.json") is True  # nosec B101


def test_validate_file_extension_invalid():
    """Test invalid file extensions are rejected."""
    assert validate_file_extension("script.sh") is False  # nosec B101
    assert validate_file_extension("executable.exe") is False  # nosec B101


def test_check_file_size_valid():
    """Test file size check within permitted threshold."""
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:  # nosec B108
        temp_file.write(b"Sample content")
        temp_path = temp_file.name

    try:
        assert check_file_size(temp_path, max_size_mb=1.0) is True  # nosec B101
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


def test_generate_file_hash():
    """Test SHA-256 generation on sample content."""
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:  # nosec B108
        temp_file.write(b"AutoAudit SHA256 Test Payload")  # pragma: allowlist secret
        temp_path = temp_file.name

    try:
        file_hash = generate_file_hash(temp_path)
        assert file_hash is not None  # nosec B101
        assert len(file_hash) == 64  # nosec B101
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


def test_process_ingestion_security_pipeline_success():
    """Test ingestion security pipeline end-to-end with valid file."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:  # nosec B108
        temp_file.write(b"Valid PDF payload data")
        temp_path = temp_file.name

    try:
        is_valid, file_hash, msg = process_ingestion_security_pipeline(temp_path)
        assert is_valid is True  # nosec B101
        assert file_hash is not None  # nosec B101
        assert "successfully validated" in msg  # nosec B101
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


def test_process_ingestion_security_pipeline_invalid_ext():
    """Test ingestion security pipeline rejects disallowed extensions."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".exe") as temp_file:  # nosec B108
        temp_file.write(b"Binary payload")
        temp_path = temp_file.name

    try:
        is_valid, file_hash, msg = process_ingestion_security_pipeline(temp_path)
        assert is_valid is False  # nosec B101
        assert file_hash is None  # nosec B101
        assert "Security Violation" in msg  # nosec B101
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


def test_process_ingestion_security_pipeline_not_found():
    """Test ingestion security pipeline handles missing files cleanly."""
    is_valid, file_hash, msg = process_ingestion_security_pipeline("missing_file.txt")
    assert is_valid is False  # nosec B101
    assert file_hash is None  # nosec B101
    assert "File not found" in msg  # nosec B101
