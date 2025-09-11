from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_ENV: str = "dev"
    API_PREFIX: str = "/api/v1"

    class Config:
        env_file = ".env"


def get_settings() -> Settings:
    return Settings()
