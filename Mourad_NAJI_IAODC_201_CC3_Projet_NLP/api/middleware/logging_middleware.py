"""
Request/Response Logging Middleware
Logs method, path, status code, and processing time for every request.
"""
from __future__ import annotations
import time
import logging
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

logger = logging.getLogger("stylist.api")


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start   = time.perf_counter()
        response = await call_next(request)
        elapsed = (time.perf_counter() - start) * 1000

        logger.info(
            f"{request.method} {request.url.path} "
            f"→ {response.status_code} "
            f"[{elapsed:.1f}ms]"
        )
        response.headers["X-Process-Time-Ms"] = f"{elapsed:.1f}"
        return response
