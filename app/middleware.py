from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from app.rate_limiter import rate_limiter


class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if not rate_limiter.enabled:
            return await call_next(request)

        path = request.url.path

        if path.startswith("/api/import/"):
            limit = rate_limiter.get_import_limit()
        elif path.startswith("/api/") and "stats" in path:
            limit = rate_limiter.get_stats_limit()
        elif path.startswith("/api/"):
            limit = rate_limiter.get_list_limit()
        elif path == "/health":
            limit = rate_limiter.get_health_limit()
        else:
            limit = 100

        rate_limiter.check_rate_limit(request, limit)

        response = await call_next(request)
        return response
