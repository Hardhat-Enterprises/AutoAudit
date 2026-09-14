"""Backend Security Ingestion Service for AutoAudit.

Handles file validation and SHA-256 cryptographic hashing.
"""

import hashlib
import os
from typing import Optional, Set, Tuple


def validate_file_extension(
    filepath: str, allowed_extensions: Optional[Set[str]] = None
) -> bool:
    """Check if the file extension is permitted based on filename."""
    if allowed_extensions is None:
        allowed_extensions = {
            ".txt",
            ".pdf",
            ".csv",
            ".json",
            ".docx",
            ".xlsx",
            ".png",
            ".jpg",
            ".jpeg",
            ".log",
            ".tif",
            ".tiff",
            ".bmp",
            ".webp",
            ".reg",
            ".ini",
            ".xml",
            ".htm",
            ".html",
        }

    _, file_extension = os.path.splitext(filepath)
    return file_extension.lower() in allowed_extensions


def check_file_size(filepath: str, max_size_mb: float = 10.0) -> bool:
    """Check if the file size is within the allowed threshold in MB."""
    try:
        max_size_bytes = max_size_mb * 1024 * 1024
        file_size_bytes = os.path.getsize(filepath)
        return file_size_bytes <= max_size_bytes
    except OSError:
        return False


def generate_file_hash_and_check_size(
    filepath: str, max_size_mb: float = 10.0
) -> Tuple[Optional[str], bool, str]:
    """Hash file contents while enforcing max size on open handle."""
    sha256_hash = hashlib.sha256()
    max_bytes = int(max_size_mb * 1024 * 1024)
    total_bytes = 0

    try:
        with open(filepath, "rb") as file_stream:  # nosec B108
            while True:
                chunk = file_stream.read(4096)
                if not chunk:
                    break
                total_bytes += len(chunk)
                if total_bytes > max_bytes:
                    msg = f"File size exceeds {max_size_mb} MB limit."
                    return None, False, msg
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest(), True, "Hashing successful."
    except OSError as err:
        return None, False, f"System Error reading file: {err}"


def generate_file_hash(filepath: str) -> Optional[str]:
    """Generate SHA-256 hash using 4096-byte chunking."""
    file_hash, within_limit, _ = generate_file_hash_and_check_size(
        filepath, max_size_mb=1000000.0
    )
    return file_hash if within_limit else None


def process_ingestion_security_pipeline(
    filepath: str,
    max_size_mb: float = 10.0,
    allowed_extensions: Optional[Set[str]] = None,
) -> Tuple[bool, Optional[str], str]:
    """Execute sequential security gates on incoming audit evidence files."""
    if not os.path.exists(filepath):
        return False, None, f"File not found: {filepath}"

    if not validate_file_extension(filepath, allowed_extensions):
        _, ext = os.path.splitext(filepath)
        return (
            False,
            None,
            f"Security Violation: Extension '{ext}' is not permitted.",
        )

    file_hash, within_limit, hash_msg = generate_file_hash_and_check_size(
        filepath, max_size_mb
    )
    if not within_limit or file_hash is None:
        return False, None, f"Security Violation: {hash_msg}"

    return True, file_hash, "File successfully validated and hashed."
