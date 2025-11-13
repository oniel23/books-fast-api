from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    api_key: str = "secret-key"

    class Config:
        env_file = ".env"


settings = Settings()
