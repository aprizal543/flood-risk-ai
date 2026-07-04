"""Authentication backend tests for Supabase-backed routes."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from fastapi.testclient import TestClient

from backend.app import app
import backend.routers.auth as auth_router
import backend.services.auth_service as auth_service


client = TestClient(app)


def test_register(monkeypatch):
    monkeypatch.setattr(
        auth_router,
        "register_user",
        lambda req: auth_service.AuthSessionResponse(
            user=auth_service.AuthUser(id="user-1", email=req.email, full_name=req.full_name),
            session=auth_service.AuthTokens(access_token="access", refresh_token="refresh"),
        ),
    )

    r = client.post(
        "/api/auth/register",
        json={"email": "user@example.com", "password": "password123", "full_name": "User A"},
    )

    assert r.status_code == 200
    assert r.json()["user"]["email"] == "user@example.com"


def test_login(monkeypatch):
    monkeypatch.setattr(
        auth_router,
        "login_user",
        lambda req: auth_service.AuthSessionResponse(
            user=auth_service.AuthUser(id="user-1", email=req.email),
            session=auth_service.AuthTokens(access_token="access", refresh_token="refresh"),
        ),
    )

    r = client.post(
        "/api/auth/login",
        json={"email": "user@example.com", "password": "password123"},
    )

    assert r.status_code == 200
    assert r.json()["session"]["access_token"] == "access"


def test_logout(monkeypatch):
    monkeypatch.setattr(auth_router, "logout_user", lambda access_token: None)

    r = client.post("/api/auth/logout", json={"access_token": "access"})

    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_refresh(monkeypatch):
    monkeypatch.setattr(
        auth_router,
        "refresh_session",
        lambda req: auth_service.AuthSessionResponse(
            user=auth_service.AuthUser(id="user-1", email="user@example.com"),
            session=auth_service.AuthTokens(access_token="new-access", refresh_token=req.refresh_token),
        ),
    )

    r = client.post("/api/auth/refresh", json={"refresh_token": "refresh"})

    assert r.status_code == 200
    assert r.json()["session"]["access_token"] == "new-access"


def test_get_current_user(monkeypatch):
    monkeypatch.setattr(
        auth_service,
        "verify_access_token",
        lambda token: auth_service.AuthUser(id="user-1", email="user@example.com", full_name="User A"),
    )
    monkeypatch.setattr("backend.dependencies.auth.verify_access_token", lambda token: auth_service.AuthUser(id="user-1", email="user@example.com", full_name="User A"))

    r = client.get("/api/auth/me", headers={"Authorization": "Bearer access"})

    assert r.status_code == 200
    assert r.json()["user"]["id"] == "user-1"


def test_unauthorized_access():
    r = client.get("/api/auth/me")
    assert r.status_code == 401


def test_invalid_token(monkeypatch):
    def raise_invalid(token: str):
        raise auth_service.AuthError("invalid token")

    monkeypatch.setattr("backend.dependencies.auth.verify_access_token", raise_invalid)

    r = client.get("/api/auth/me", headers={"Authorization": "Bearer bad-token"})

    assert r.status_code == 401


def test_expired_token(monkeypatch):
    def raise_expired(token: str):
        raise auth_service.AuthError("expired token")

    monkeypatch.setattr("backend.dependencies.auth.verify_access_token", raise_expired)

    r = client.get("/api/auth/me", headers={"Authorization": "Bearer expired-token"})

    assert r.status_code == 401
