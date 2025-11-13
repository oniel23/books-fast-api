"""Application configuration settings."""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Settings loaded from environment variables."""

    api_key: str = "secret-key"

    class Config:
        env_file = ".env"


settings = Settings()
