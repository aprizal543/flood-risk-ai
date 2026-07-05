"""Authentication routes backed by Supabase Auth."""

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel

from backend.dependencies.auth import get_current_user
from backend.schemas.response import ErrorResponse
from backend.security.limits import LOGIN_LIMIT, REGISTER_LIMIT
from backend.security.rate_limit import limiter
from backend.services.auth_service import (
    AuthError,
    AuthLoginRequest,
    AuthRefreshRequest,
    AuthRegisterRequest,
    AuthSessionResponse,
    AuthUser,
    login_user,
    logout_user,
    refresh_session,
    register_user,
)

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


class LogoutRequest(BaseModel):
    access_token: str


class CurrentUserResponse(BaseModel):
    user: AuthUser


@router.post("/register", response_model=AuthSessionResponse, responses={400: {"model": ErrorResponse}, 422: {"model": ErrorResponse}})
@limiter.limit(REGISTER_LIMIT)
def register(request: Request, req: AuthRegisterRequest) -> AuthSessionResponse:
    try:
        return register_user(req)
    except AuthError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@router.post("/login", response_model=AuthSessionResponse, responses={401: {"model": ErrorResponse}, 422: {"model": ErrorResponse}})
@limiter.limit(LOGIN_LIMIT)
def login(request: Request, req: AuthLoginRequest) -> AuthSessionResponse:
    try:
        return login_user(req)
    except AuthError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc))


@router.post("/logout", response_model=dict, responses={401: {"model": ErrorResponse}})
def logout(req: LogoutRequest) -> dict:
    try:
        logout_user(req.access_token)
    except AuthError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc))
    return {"status": "ok"}


@router.get("/me", response_model=CurrentUserResponse, responses={401: {"model": ErrorResponse}})
def me(current_user: AuthUser = Depends(get_current_user)) -> CurrentUserResponse:
    return CurrentUserResponse(user=current_user)


@router.post("/refresh", response_model=AuthSessionResponse, responses={401: {"model": ErrorResponse}, 422: {"model": ErrorResponse}})
def refresh(req: AuthRefreshRequest) -> AuthSessionResponse:
    try:
        return refresh_session(req)
    except AuthError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc))



