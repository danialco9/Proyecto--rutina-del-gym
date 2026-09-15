"""Cookie-based authentication endpoints."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Response, status

from gym_tracker.api.deps import ACCESS_TOKEN_COOKIE, CurrentUser, SessionDep, SettingsDep
from gym_tracker.schemas import LoginRequest, UserRead
from gym_tracker.security import create_access_token
from gym_tracker.users import authenticate

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", status_code=status.HTTP_204_NO_CONTENT)
def login(credentials: LoginRequest, response: Response, session: SessionDep, settings: SettingsDep) -> None:
    user = authenticate(session, email=credentials.email, password=credentials.password)
    if user is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    response.set_cookie(
        ACCESS_TOKEN_COOKIE,
        create_access_token(str(user.id), settings),
        max_age=settings.access_token_ttl_minutes * 60,
        httponly=True,
        secure=settings.cookie_secure,
        samesite="lax",
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(response: Response, settings: SettingsDep) -> None:
    response.delete_cookie(ACCESS_TOKEN_COOKIE, httponly=True, secure=settings.cookie_secure, samesite="lax")


@router.get("/me")
def read_current_user(user: CurrentUser) -> UserRead:
    return UserRead.model_validate(user)
