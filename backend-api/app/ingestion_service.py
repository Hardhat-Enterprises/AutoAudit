"""Backend Security Ingestion Service for AutoAudit.

Handles file validation (extension and size checks) and SHA-256 cryptographic hashing.
"""

import hashlib
import os
from typing import Optional, Tuple


def validate_file_extension(filepath: str, allowed_extensions: Optional[set] = None) -> bool:
    """Checks if the file extension is permitted based on filename.

    Note: Extension validation checks filename structure only, not binary content.
    """
    if allowed_extensions is None:
        allowed_extensions = {".txt", ".pdf", ".csv", ".json", ".docx", ".xlsx"}

    _, file_extension = os.path.splitext(filepath)
    return file_extension.lower() in allowed_extensions


def check_file_size(filepath: str, max_size_mb: float = 10.0) -> bool:
    """Checks if the file size is within the allowed threshold in MB."""
    try:
        max_size_bytes = max_size_mb * 1024 * 1024
        file_size_bytes = os.path.getsize(filepath)
        return file_size_bytes <= max_size_bytes
    except OSError:
        return False


def generate_file_hash(filepath: str) -> Optional[str]:
    """Generates a SHA-256 hash using 4096-byte chunking for safe memory management."""
    sha256_hash = hashlib.sha256()
    try:
        with open(filepath, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except OSError:
        return None


def process_ingestion_security_pipeline(
    filepath: str,
    max_size_mb: float = 10.0,
    allowed_extensions: Optional[set] = None,
) -> Tuple[bool, Optional[str], str]:
    """Executes sequential security gates on incoming audit evidence files.

    Returns:
        Tuple[bool, Optional[str], str]: (success_status, sha256_hash, log_message)
    """
    if not os.path.exists(filepath):
        return False, None, f"File not found: {filepath}"

    if not validate_file_extension(filepath, allowed_extensions):
        _, ext = os.path.splitext(filepath)
        return False, None, f"Security Violation: Extension '{ext}' is not permitted."

    try:
        if not check_file_size(filepath, max_size_mb):
            return False, None, f"Security Violation: File size exceeds {max_size_mb} MB limit."
    except OSError as e:
        return False, None, f"System Error: Unable to inspect file size ({e})."

    file_hash = generate_file_hash(filepath)
    if file_hash is None:
        return False, None, "System Error: Unable to read file contents for hashing."

    return True, file_hash, "File successfully validated and hashed."
