"""Middleware for request/response tracking, RequestID, and security headers."""

import logging
import time

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from backend.logging import generate_request_id, set_request_id

logger = logging.getLogger("backend")


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = generate_request_id()
        set_request_id(request_id)

        start = time.perf_counter()
        path = request.url.path
        query = request.url.query
        full_path = f"{path}?{query}" if query else path
        logger.info("[%s] Request: %s %s", request_id, request.method, full_path)

        response = await call_next(request)

        elapsed = (time.perf_counter() - start) * 1000
        logger.info(
            "[%s] Response: %s (%dms)",
            request_id,
            response.status_code,
            elapsed,
        )
        return response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        return response
