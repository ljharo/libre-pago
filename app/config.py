from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="allow")

    db_user: str = "postgres"
    db_password: str = "postgres"
    db_host: str = "localhost"
    db_port: str = "5432"
    db_name: str = "librepago"

    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0

    rate_limit_enabled: bool = True
    rate_limit_import: int = 20
    rate_limit_list: int = 60
    rate_limit_stats: int = 30
    rate_limit_health: int = 200
    rate_limit_window: int = 60

    cache_enabled: bool = True
    cache_ttl_stats: int = 300
    cache_ttl_list: int = 60
    cache_ttl_mappings: int = 3600

    log_level: str = "INFO"
    log_format: str = "json"

    api_key: str = "default-api-key-change-me"
    app_name: str = "LibrePago API"
    debug: bool = False

    @property
    def database_url(self) -> str:
        return f"postgresql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"

    @property
    def redis_url(self) -> str:
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"


settings = Settings()
