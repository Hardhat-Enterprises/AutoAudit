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


def test_process_ingestion_pipeline_valid():
    with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as tmp:
        tmp.write(b'{"test": "data"}')
        tmp_path = tmp.name

    is_valid, file_hash, error = process_ingestion_security_pipeline(tmp_path)
    assert is_valid is True
    assert len(file_hash) == 64
    assert error == ""
