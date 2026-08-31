"""
app/services/ingestion_service.py

Backend Security Ingestion Service for AutoAudit.
Handles file validation (extension and size checks) and SHA-256 cryptographic hashing.
"""

import os
import hashlib
from typing import Tuple, Optional


def validate_file_extension(filepath: str, allowed_extensions: Optional[set] = None) -> bool:
    """Checks if the file extension is permitted."""
    if allowed_extensions is None:
        allowed_extensions = {'.txt', '.pdf', '.csv', '.json', '.docx', '.xlsx'}
        
    _, file_extension = os.path.splitext(filepath)
    return file_extension.lower() in allowed_extensions


def check_file_size(filepath: str, max_size_mb: float = 10.0) -> bool:
    """Checks if the file size is within the allowed threshold in MB."""
    max_size_bytes = max_size_mb * 1024 * 1024
    file_size_bytes = os.path.getsize(filepath)
    return file_size_bytes <= max_size_bytes


def generate_file_hash(filepath: str) -> str:
    """Generates a SHA-256 hash using 4096-byte chunking for safe memory management."""
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def process_ingestion_security_pipeline(
    filepath: str, 
    max_size_mb: float = 10.0, 
    allowed_extensions: Optional[set] = None
) -> Tuple[bool, Optional[str], str]:
    """
    Executes sequential security gates on incoming audit files.
    
    Returns:
        Tuple[bool, Optional[str], str]: (success_status, sha256_hash, log_message)
    """
    if not os.path.exists(filepath):
        return False, None, f"File not found: {filepath}"

    if not validate_file_extension(filepath, allowed_extensions):
        _, ext = os.path.splitext(filepath)
        return False, None, f"Security Violation: Extension '{ext}' is not permitted."

    if not check_file_size(filepath, max_size_mb):
        return False, None, f"Security Violation: File size exceeds {max_size_mb} MB limit."

    file_hash = generate_file_hash(filepath)
    return True, file_hash, "File successfully validated and hashed."
