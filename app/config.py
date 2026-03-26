from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    db_user: str = "postgres"
    db_password: str = "postgres"
    db_host: str = "localhost"
    db_port: str = "5432"
    db_name: str = "librepago"

    api_key: str = "default-api-key-change-me"
    app_name: str = "LibrePago API"
    debug: bool = False

    @property
    def database_url(self) -> str:
        return f"postgresql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"

    class Config:
        env_file = ".env"
        extra = "allow"


settings = Settings()
