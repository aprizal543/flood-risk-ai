"""Rate-limiting infrastructure using SlowAPI.

Provides the shared Limiter instance, client-IP key function,
and a FastAPI 429 exception handler.

Usage:
    from backend.security.rate_limit import limiter

    @router.get("/example")
    @limiter.limit("5/minute")
    async def example(request: Request):
        ...
"""

from __future__ import annotations

from fastapi import Request
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from backend.dependencies.auth import bearer_scheme
from backend.services.auth_service import AuthError, verify_access_token


def _ip_key_func(request: Request) -> str:
    """Return the client IP address as the rate-limit key.

    Uses X-Forwarded-For when behind a reverse proxy,
    falling back to the direct remote address.
    """
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return get_remote_address(request)


def _user_or_ip_key_func(request: Request) -> str:
    """Return the authenticated user ID as the rate-limit key.

    Falls back to client IP when no authenticated user is found.
    The user ID is injected into request.state by an optional
    auth dependency in the route handler.
    """
    user_id = getattr(request.state, "user_id", None)
    if user_id:
        return f"user:{user_id}"
    return _ip_key_func(request)


async def _optional_auth_dependency(request: Request) -> None:
    """Optional FastAPI dependency that sets request.state.user_id.

    If a valid Bearer token is present, the user ID is extracted
    and stored on request.state for the rate-limit key function.
    If no token is present or the token is invalid, silently continues — no 401 raised.
    """
    credentials = await bearer_scheme(request)
    if credentials is None or not credentials.credentials:
        return
    try:
        user = verify_access_token(credentials.credentials)
        request.state.user_id = user.id
    except AuthError:
        pass


limiter = Limiter(key_func=_user_or_ip_key_func)


async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    """Return a consistent JSON response on 429 Too Many Requests.

    Follows the same error format used elsewhere in this API.
    """
    return JSONResponse(
        status_code=429,
        content={
            "status": "error",
            "kode": 429,
            "pesan": "Terlalu banyak permintaan. Silakan coba lagi nanti.",
        },
    )
