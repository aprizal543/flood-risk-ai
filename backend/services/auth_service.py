"""Authentication service backed by Supabase Auth."""

from __future__ import annotations

import os
from typing import Any

import httpx
from pydantic import BaseModel, Field


class AuthError(RuntimeError):
    """Raised when Supabase Auth rejects a request."""


class AuthTokens(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int | None = None


class AuthUser(BaseModel):
    id: str
    email: str | None = None
    role: str | None = None
    full_name: str | None = None
    avatar_url: str | None = None


class AuthSessionResponse(BaseModel):
    user: AuthUser
    session: AuthTokens | None = None


class AuthRegisterRequest(BaseModel):
    email: str = Field(min_length=3, max_length=254)
    password: str = Field(min_length=6, max_length=72)
    full_name: str = Field(default="", max_length=200)


class AuthLoginRequest(BaseModel):
    email: str = Field(min_length=3, max_length=254)
    password: str = Field(min_length=6, max_length=72)


class AuthRefreshRequest(BaseModel):
    refresh_token: str = Field(min_length=1)


def _supabase_url() -> str:
    url = os.getenv("SUPABASE_URL")
    if not url:
        raise RuntimeError("SUPABASE_URL is not configured")
    return url.rstrip("/")


def _anon_key() -> str:
    key = os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY") or os.getenv("SUPABASE_ANON_KEY")
    if not key:
        raise RuntimeError("Supabase anon key is not configured")
    return key


def _headers() -> dict[str, str]:
    return {
        "apikey": _anon_key(),
        "Content-Type": "application/json",
    }


def _request(method: str, path: str, *, json_body: dict[str, Any] | None = None, access_token: str | None = None) -> dict[str, Any]:
    headers = _headers()
    if access_token:
        headers["Authorization"] = f"Bearer {access_token}"

    url = f"{_supabase_url()}{path}"
    with httpx.Client(timeout=15.0) as client:
        response = client.request(method, url, headers=headers, json=json_body)

    if response.status_code >= 400:
        message = response.text
        try:
            data = response.json()
            message = data.get("msg") or data.get("message") or data.get("error_description") or message
        except ValueError:
            pass
        raise AuthError(message)

    return response.json()


def _extract_user(payload: dict[str, Any]) -> AuthUser:
    user = payload.get("user") or payload
    metadata = user.get("user_metadata") or {}
    return AuthUser(
        id=user["id"],
        email=user.get("email"),
        role=user.get("role"),
        full_name=metadata.get("full_name"),
        avatar_url=metadata.get("avatar_url"),
    )


def _extract_session(payload: dict[str, Any]) -> AuthTokens:
    session = payload.get("session") or payload
    if not isinstance(session, dict) or "access_token" not in session or "refresh_token" not in session:
        raise AuthError("Session tidak tersedia dari Supabase Auth.")
    return AuthTokens(
        access_token=session["access_token"],
        refresh_token=session["refresh_token"],
        token_type=session.get("token_type", "bearer"),
        expires_in=session.get("expires_in"),
    )


def register_user(data: AuthRegisterRequest) -> AuthSessionResponse:
    payload = {
        "email": data.email,
        "password": data.password,
        "data": {"full_name": data.full_name},
    }
    result = _request("POST", "/auth/v1/signup", json_body=payload)
    user = _extract_user(result)
    session = None
    if result.get("session") is not None:
        try:
            session = _extract_session(result)
        except AuthError:
            session = None
    return AuthSessionResponse(user=user, session=session)


def login_user(data: AuthLoginRequest) -> AuthSessionResponse:
    payload = {"email": data.email, "password": data.password}
    result = _request("POST", "/auth/v1/token?grant_type=password", json_body=payload)
    user = _extract_user(result)
    session = _extract_session(result)
    return AuthSessionResponse(user=user, session=session)


def logout_user(access_token: str) -> None:
    _request("POST", "/auth/v1/logout", access_token=access_token)


def refresh_session(data: AuthRefreshRequest) -> AuthSessionResponse:
    payload = {"refresh_token": data.refresh_token}
    result = _request("POST", "/auth/v1/token?grant_type=refresh_token", json_body=payload)
    user = _extract_user(result)
    session = _extract_session(result)
    return AuthSessionResponse(user=user, session=session)


def verify_access_token(access_token: str) -> AuthUser:
    result = _request("GET", "/auth/v1/user", access_token=access_token)
    return _extract_user(result)



