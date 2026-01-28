from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # The below settings are defaults, and not duplicates of .env
    # The contents of .env overrides what is defined here.
    APP_ENV: str = "dev"
    API_PREFIX: str = "/v1"

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://autoaudit:autoaudit_dev_password@localhost:5432/autoaudit"

    # Authentication
    SECRET_KEY: str = "change-this-to-a-secure-random-string-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Public URLs (used for OAuth redirects)
    # These must be the externally reachable URLs (e.g. localhost from the browser).
    BACKEND_PUBLIC_URL: str = "http://localhost:8000"
    FRONTEND_URL: str = "http://localhost:3000"

    # Google OAuth (SSO)
    GOOGLE_OAUTH_CLIENT_ID: str = ""
    GOOGLE_OAUTH_CLIENT_SECRET: str = ""

    # Redis (for Celery broker)
    REDIS_URL: str = "redis://localhost:6379"

    # OPA (Open Policy Agent)
    OPA_URL: str = "http://localhost:8181"

    # Encryption (for securing credentials at rest)
    # Generate with: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
    ENCRYPTION_KEY: str = ""

    # Policies directory (for benchmark/control metadata)
    POLICIES_DIR: str = "/app/policies"

    class Config:
        env_file = ".env"


def get_settings() -> Settings:
    return Settings()
