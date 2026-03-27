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
        # Override with environment variables (uppercase)
        env_mappings = {
            "db_user": os.environ.get("DB_USER") or "postgres",
            "db_password": os.environ.get("DB_PASSWORD") or "postgres",
            "db_host": os.environ.get("DB_HOST") or "localhost",
            "db_port": int(os.environ.get("DB_PORT") or "5432"),
            "db_name": os.environ.get("DB_NAME") or "librepago",
            "redis_host": os.environ.get("REDIS_HOST") or "localhost",
            "redis_port": int(os.environ.get("REDIS_PORT") or "6379"),
            "redis_db": int(os.environ.get("REDIS_DB") or "0"),
            "api_key": os.environ.get("API_KEY") or "default-api-key",
            "jwt_secret": os.environ.get("JWT_SECRET") or "change-me",
            "jwt_algorithm": os.environ.get("JWT_ALGORITHM") or "HS256",
            "jwt_expire_days": int(os.environ.get("JWT_EXPIRE_DAYS") or "1"),
            "admin_username": os.environ.get("ADMIN_USERNAME") or "admin",
            "admin_password": os.environ.get("ADMIN_PASSWORD") or "admin123",
            "debug": (os.environ.get("DEBUG") or "false").lower() == "true",
            "log_level": os.environ.get("LOG_LEVEL") or "INFO",
            "log_format": os.environ.get("LOG_FORMAT") or "json",
            "rate_limit_enabled": (os.environ.get("RATE_LIMIT_ENABLED") or "false").lower() == "true",
            "cache_enabled": (os.environ.get("CACHE_ENABLED") or "false").lower() == "true",
        }
        kwargs.update(env_mappings)
        super().__init__(**kwargs)

    @property
    def database_url(self) -> str:
        return f"postgresql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"

    @property
    def redis_url(self) -> str:
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"


settings = Settings()
