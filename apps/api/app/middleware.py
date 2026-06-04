from __future__ import annotations

import logging
import time
import uuid
from collections import defaultdict, deque
from typing import Deque

from fastapi import HTTPException, Request, Response, status
from starlette.middleware.base import BaseHTTPMiddleware

from .config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# In-memory rate limiter (per-process)
_request_windows: dict[str, Deque[float]] = defaultdict(deque)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response: Response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        response.headers["Cross-Origin-Opener-Policy"] = "same-origin"
        forwarded = request.headers.get("x-forwarded-proto")
        if forwarded == "https":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        return response


class RequestIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())[:8]
        request.state.request_id = request_id
        start = time.perf_counter()
        response: Response = await call_next(request)
        elapsed = round((time.perf_counter() - start) * 1000, 1)
        response.headers["X-Request-Id"] = request_id
        logger.info(
            "%s %s %s %sms",
            request.method,
            request.url.path,
            response.status_code,
            elapsed,
            extra={"request_id": request_id},
        )
        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        client_host = request.client.host if request.client else "unknown"
        key = f"{client_host}:{request.url.path}"
        now = time.time()
        window = _request_windows[key]
        threshold = now - settings.rate_limit_window_seconds

        while window and window[0] < threshold:
            window.popleft()

        if len(window) >= settings.rate_limit_requests:
            return Response(
                content='{"detail":"Rate limit exceeded."}',
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                media_type="application/json",
                headers={"Retry-After": str(settings.rate_limit_window_seconds)},
            )

        window.append(now)
        return await call_next(request)
