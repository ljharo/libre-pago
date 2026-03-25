import os

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = os.environ.get("DATABASE_URL", "sqlite:///./librepago.db")
    api_key: str = os.environ.get("API_KEY", "default-api-key-change-me")
    app_name: str = "LibrePago API"
    debug: bool = os.environ.get("DEBUG", "false").lower() == "true"

    class Config:
        env_file = ".env"
        extra = "allow"


settings = Settings()
