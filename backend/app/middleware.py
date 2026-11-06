"""Simple in-memory sliding-window rate limiter (per client IP) for /api/* routes.
For multi-instance production use a shared store (Redis) instead."""
import time
from collections import defaultdict, deque

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, per_minute=30):
        super().__init__(app)
        self.per_minute = per_minute
        self.hits = defaultdict(deque)

    async def dispatch(self, request: Request, call_next):
        if request.url.path.startswith("/api/") and request.method != "OPTIONS" and self.per_minute > 0:
            fwd = request.headers.get("x-forwarded-for", "")
            ip = fwd.split(",")[0].strip() or (request.client.host if request.client else "unknown")
            now = time.time()
            q = self.hits[ip]
            while q and now - q[0] > 60:
                q.popleft()
            if len(q) >= self.per_minute:
                return JSONResponse({"detail": "Too many requests. Please wait a minute."},
                                    status_code=429, headers={"Retry-After": "60"})
            q.append(now)
        return await call_next(request)
