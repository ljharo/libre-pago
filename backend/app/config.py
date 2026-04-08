import os

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="allow")

    db_user: str = "postgres"
    db_password: str = "postgres"
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "librepago"

    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0

    rate_limit_enabled: bool = False
    rate_limit_import: int = 20
    rate_limit_list: int = 1000
    rate_limit_stats: int = 30
    rate_limit_health: int = 200
    rate_limit_window: int = 60

    cache_enabled: bool = False
    cache_ttl_stats: int = 300
    cache_ttl_list: int = 60
    cache_ttl_mappings: int = 3600

    log_level: str = "INFO"
    log_format: str = "json"

    api_key: str = "default-api-key-change-me"
    app_name: str = "LibrePago API"
    debug: bool = False

    admin_username: str = "admin"
    admin_password: str = "admin123"
    jwt_secret: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_days: int = 1

    def __init__(self, **kwargs):
        # Merge environment variables (uppercase) with .env file values
        # Priority: explicit kwargs > env vars > .env file > defaults
        env_vars = {
            "DB_USER",
            "DB_PASSWORD",
            "DB_HOST",
            "DB_PORT",
            "DB_NAME",
            "REDIS_HOST",
            "REDIS_PORT",
            "REDIS_DB",
            "API_KEY",
            "DEBUG",
            "LOG_LEVEL",
            "LOG_FORMAT",
            "JWT_SECRET",
            "JWT_ALGORITHM",
            "JWT_EXPIRE_DAYS",
            "ADMIN_USERNAME",
            "ADMIN_PASSWORD",
            "RATE_LIMIT_ENABLED",
            "RATE_LIMIT_IMPORT",
            "CACHE_ENABLED",
        }

        for key in env_vars:
            env_key = key.lower()
            if env_key not in kwargs and os.environ.get(key):
                kwargs[env_key] = os.environ.get(key)

        super().__init__(**kwargs)

    @property
    def database_url(self) -> str:
        return f"postgresql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"

    @property
    def redis_url(self) -> str:
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"


settings = Settings()
