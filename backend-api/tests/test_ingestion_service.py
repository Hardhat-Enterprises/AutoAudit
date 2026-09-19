"""Unit tests for the ingestion security pipeline."""

import tempfile
import pytest
from app.ingestion_service import (
    calculate_sha256,
    process_ingestion_security_pipeline,
    validate_file_extension,
)


def test_validate_file_extension():
    assert validate_file_extension("test.pdf") is True
    assert validate_file_extension("test.exe") is False
    assert validate_file_extension("test.sh") is False


def test_calculate_sha256():
    with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as tmp:
        tmp.write(b"AutoAudit Test Content")
        tmp_path = tmp.name

    hash_val = calculate_sha256(tmp_path)
    assert isinstance(hash_val, str)
    assert len(hash_val) == 64


def test_calculate_sha256_oversized():
    with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as tmp:
        tmp.write(b"1234567890")
        tmp_path = tmp.name

    with pytest.raises(ValueError, match="Security Violation"):
        calculate_sha256(tmp_path, max_bytes=5)


def test_process_ingestion_pipeline_valid():
    with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as tmp:
        tmp.write(b'{"test": "data"}')
        tmp_path = tmp.name

    is_valid, file_hash, error = process_ingestion_security_pipeline(tmp_path)
    assert is_valid is True
    assert len(file_hash) == 64
    assert error == ""


def test_process_ingestion_pipeline_missing_file():
    is_valid, file_hash, error = process_ingestion_security_pipeline("non_existent_file.pdf")
    assert is_valid is False
    assert file_hash == ""
    assert "File not found" in error


def test_process_ingestion_pipeline_invalid_extension():
    with tempfile.NamedTemporaryFile(delete=False, suffix=".exe") as tmp:
        tmp.write(b"binary data")
        tmp_path = tmp.name

    is_valid, file_hash, error = process_ingestion_security_pipeline(tmp_path)
    assert is_valid is False
    assert file_hash == ""
    assert "Unpermitted file extension" in error


def test_process_ingestion_pipeline_oversized():
    with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as tmp:
        tmp.write(b"a" * 100)
        tmp_path = tmp.name

    is_valid, file_hash, error = process_ingestion_security_pipeline(tmp_path, max_bytes=50)
    assert is_valid is False
    assert file_hash == ""
    assert "exceeds maximum allowed limit" in error
