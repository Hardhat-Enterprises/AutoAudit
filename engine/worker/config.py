"""Configuration for the Celery worker."""

import os

from pydantic_settings import BaseSettings


class WorkerSettings(BaseSettings):
    """Worker configuration loaded from environment variables."""

    # Database
    DATABASE_URL: str = "postgresql://autoaudit:autoaudit_dev_password@localhost:5432/autoaudit"  # pragma: allowlist secret

    # Redis (Celery broker)
    REDIS_URL: str = "redis://localhost:6379/0"

    # OPA (Open Policy Agent)
    OPA_URL: str = "http://localhost:8181"

    # Encryption key for decrypting credentials
    ENCRYPTION_KEY: str = ""

    # Policies directory
    POLICIES_DIR: str = os.path.join(os.path.dirname(__file__), "..", "policies")

    # PowerShell service URL (optional - if set, uses HTTP instead of Docker)
    POWERSHELL_SERVICE_URL: str | None = None

    # SharePoint PnP (optional). Used only when constructing PowerShellClient.
    # Admin URL is tenant-specific and cannot be derived from tenant_id GUID.
    SHAREPOINT_ADMIN_URL: str | None = None
    # Certificate alias resolved by the PowerShell service SHAREPOINT_CERT_ALIASES map.
    # V1 uses a single mounted alias.
    SHAREPOINT_CERT_ALIAS: str = "default"

    # Performance mode: PowerShell-based controls (Exchange/Compliance/Teams) are much slower
    # than Graph-based controls. Default is True to preserve full scan coverage.
    ENABLE_POWERSHELL_CONTROLS: bool = True

    class Config:
        env_file = ".env"


def get_settings() -> WorkerSettings:
    """Get worker settings instance."""
    return WorkerSettings()


settings = get_settings()
