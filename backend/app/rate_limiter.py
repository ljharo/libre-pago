from collections.abc import Callable

import redis
from fastapi import HTTPException, Request

from app.config import settings


class RateLimiter:
    def __init__(self):
        self.redis_client = None
        self.enabled = settings.rate_limit_enabled
        self.window = settings.rate_limit_window
        if self.enabled:
            try:
                self.redis_client = redis.Redis.from_url(settings.redis_url)
                self.redis_client.ping()
            except Exception:
                self.redis_client = None
                self.enabled = False

    def _get_client_key(self, request: Request) -> str:
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            client_ip = forwarded.split(",")[0].strip()
        else:
            client_ip = request.client.host if request.client else "unknown"
        return f"ratelimit:{client_ip}"

    def check_rate_limit(self, request: Request, limit: int) -> None:
        if not self.enabled or not self.redis_client:
            return

        key = self._get_client_key(request)
        current = self.redis_client.get(key)

        if current and int(current) >= limit:
            raise HTTPException(
                status_code=429,
                detail=f"Rate limit exceeded. Try again in {self.window} seconds.",
            )

        pipe = self.redis_client.pipeline()
        pipe.incr(key)
        if not current:
            pipe.expire(key, self.window)
        pipe.execute()

    def get_import_limit(self) -> int:
        return settings.rate_limit_import

    def get_list_limit(self) -> int:
        return settings.rate_limit_list

    def get_stats_limit(self) -> int:
        return settings.rate_limit_stats

    def get_health_limit(self) -> int:
        return settings.rate_limit_health


rate_limiter = RateLimiter()


def rate_limit_dependency(limit: int) -> Callable:
    def check(request: Request):
        if settings.rate_limit_enabled:
            rate_limiter.check_rate_limit(request, limit)
        return "ok"

    return check
