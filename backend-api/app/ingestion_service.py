"""Ingestion Service Module for Cryptographic File Hashing and Validation."""

import hashlib
import os
from typing import Tuple

ALLOWED_EXTENSIONS = {".txt", ".pdf", ".png", ".jpg", ".jpeg", ".json", ".csv"}


def validate_file_extension(filename: str) -> bool:
    _, ext = os.path.splitext(filename)
    return ext.lower() in ALLOWED_EXTENSIONS


def calculate_sha256(file_path: str) -> str:
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def process_ingestion_security_pipeline(file_path: str) -> Tuple[bool, str, str]:
    if not os.path.exists(file_path):
        return False, "", "File not found."

    if not validate_file_extension(file_path):
        return False, "", "Security Violation: Unpermitted file extension."

    try:
        file_hash = calculate_sha256(file_path)
        return True, file_hash, ""
    except Exception as e:
        return False, "", f"Processing error: {str(e)}"
