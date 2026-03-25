from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "sqlite:///./librepago.db"
    api_key: str = "default-api-key-change-me"
    app_name: str = "LibrePago API"
    debug: bool = False

    class Config:
        env_file = ".env"
        extra = "allow"


settings = Settings()
