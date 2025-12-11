"""Configuration for the Celery worker."""

import os

from pydantic_settings import BaseSettings


class WorkerSettings(BaseSettings):
    """Worker configuration loaded from environment variables."""

    # Database
    DATABASE_URL: str = "postgresql://autoaudit:autoaudit_dev_password@localhost:5432/autoaudit"

    # Redis (Celery broker)
    REDIS_URL: str = "redis://localhost:6379/0"

    # OPA (Open Policy Agent)
    OPA_URL: str = "http://localhost:8181"

    # Encryption key for decrypting credentials
    ENCRYPTION_KEY: str = ""

    # Policies directory
    POLICIES_DIR: str = os.path.join(os.path.dirname(__file__), "..", "policies")

    class Config:
        env_file = ".env"


def get_settings() -> WorkerSettings:
    """Get worker settings instance."""
    return WorkerSettings()


settings = get_settings()
