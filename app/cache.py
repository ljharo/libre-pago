import hashlib
import json
from collections.abc import Callable
from functools import wraps
from typing import Any

import redis
from fastapi import Request

from app.config import settings


class CacheManager:
    def __init__(self):
        self.redis_client = None
        self.enabled = settings.cache_enabled
        if self.enabled:
            try:
                self.redis_client = redis.Redis.from_url(settings.redis_url)
                self.redis_client.ping()
            except Exception:
                self.redis_client = None
                self.enabled = False

    def _generate_key(self, prefix: str, request: Request, extra: str = "") -> str:
        key_parts = [
            prefix,
            request.url.path,
            str(request.query_params),
            extra,
        ]
        key_str = ":".join(key_parts)
        return f"cache:{hashlib.md5(key_str.encode()).hexdigest()}"

    def get(self, key: str) -> Any | None:
        if not self.enabled or not self.redis_client:
            return None
        try:
            data = self.redis_client.get(key)
            if data:
                return json.loads(data)
        except Exception:
            pass
        return None

    def set(self, key: str, value: Any, ttl: int) -> None:
        if not self.enabled or not self.redis_client:
            return
        try:
            self.redis_client.setex(key, ttl, json.dumps(value))
        except Exception:
            pass

    def invalidate_pattern(self, pattern: str) -> None:
        if not self.enabled or not self.redis_client:
            return
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                self.redis_client.delete(*keys)
        except Exception:
            pass


cache_manager = CacheManager()


def cache_response(prefix: str, ttl: int = 60):
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(request: Request, *args, **kwargs):
            if not settings.cache_enabled:
                return await func(request, *args, **kwargs)

            cache_key = cache_manager._generate_key(prefix, request)
            cached_data = cache_manager.get(cache_key)

            if cached_data is not None:
                return cached_data

            result = await func(request, *args, **kwargs)

            if result is not None:
                cache_manager.set(cache_key, result, ttl)

            return result

        return wrapper

    return decorator


def get_stats_cache_ttl() -> int:
    return settings.cache_ttl_stats


def get_list_cache_ttl() -> int:
    return settings.cache_ttl_list


def get_mappings_cache_ttl() -> int:
    return settings.cache_ttl_mappings
