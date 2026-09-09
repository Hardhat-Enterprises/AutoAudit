import os
import sys
import tempfile
import pytest

# Fix module resolution so Pytest locates the app package during CI/CD execution
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.services.ingestion_service import (
    check_file_size,
    generate_file_hash,
    process_ingestion_security_pipeline,
    validate_file_extension,
)


@pytest.fixture
def temp_test_file():
    """Creates a temporary valid text file for testing."""
    with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as tf:
        tf.write(b"AutoAudit Test Content")
        temp_path = tf.name
    yield temp_path
    if os.path.exists(temp_path):
        os.remove(temp_path)


def test_validate_file_extension_allowed(temp_test_file):
    assert validate_file_extension(temp_test_file) is True


def test_validate_file_extension_disallowed():
    assert validate_file_extension("malicious_script.exe") is False


def test_check_file_size_within_limit(temp_test_file):
    assert check_file_size(temp_test_file, max_size_mb=1.0) is True


def test_check_file_size_exceeding_limit(temp_test_file):
    assert check_file_size(temp_test_file, max_size_mb=0.000001) is False


def test_missing_file():
    success, hash_val, msg = process_ingestion_security_pipeline("non_existent_file.pdf")
    assert success is False
    assert hash_val is None
    assert "File not found" in msg


def test_successful_pipeline_execution(temp_test_file):
    success, hash_val, msg = process_ingestion_security_pipeline(temp_test_file)
    assert success is True
    assert hash_val is not None
    assert len(hash_val) == 64
    assert "successfully validated" in msg


def test_hash_generation(temp_test_file):
    digest = generate_file_hash(temp_test_file)
    assert digest is not None
    assert isinstance(digest, str)
    assert len(digest) == 64
