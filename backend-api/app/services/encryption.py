"""Encryption service for securing sensitive data at rest.

Uses Fernet symmetric encryption. The encryption key must be a 32-byte
base64-encoded key, provided via the ENCRYPTION_KEY environment variable.

Generate a key with: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
"""

from cryptography.fernet import Fernet, InvalidToken

from app.core.config import get_settings

_fernet: Fernet | None = None


def get_fernet() -> Fernet:
    """Get or create the Fernet encryption instance."""
    global _fernet
    if _fernet is None:
        settings = get_settings()
        if not settings.ENCRYPTION_KEY:
            raise ValueError(
                "ENCRYPTION_KEY environment variable is required. "
                "Generate one with: python -c \"from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())\""
            )
        _fernet = Fernet(settings.ENCRYPTION_KEY.encode())
    return _fernet


def encrypt(plaintext: str) -> str:
    """Encrypt a string and return the ciphertext as a string.

    Args:
        plaintext: The string to encrypt.

    Returns:
        The encrypted string (base64-encoded).
    """
    if not plaintext:
        return ""
    return get_fernet().encrypt(plaintext.encode()).decode()


def decrypt(ciphertext: str) -> str:
    """Decrypt a ciphertext string and return the plaintext.

    Args:
        ciphertext: The encrypted string (base64-encoded).

    Returns:
        The decrypted plaintext string.

    Raises:
        InvalidToken: If the ciphertext is invalid or the key is wrong.
    """
    if not ciphertext:
        return ""
    return get_fernet().decrypt(ciphertext.encode()).decode()
