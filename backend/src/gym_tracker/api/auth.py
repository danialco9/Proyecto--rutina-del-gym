"""Cookie-based authentication endpoints."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Response, status

from gym_tracker.api.common import commit_or_conflict
from gym_tracker.api.deps import (
    ACCESS_TOKEN_COOKIE,
    ClientAddress,
    CurrentUser,
    RateLimiterDep,
    SessionDep,
    SettingsDep,
)
from gym_tracker.config import Settings
from gym_tracker.rate_limit import LOGIN_PER_CLIENT_AND_EMAIL, LOGIN_PER_EMAIL, REGISTER_PER_CLIENT, Check
from gym_tracker.schemas import LoginRequest, RegisterRequest, UserRead
from gym_tracker.security import create_access_token
from gym_tracker.users import UserAlreadyExistsError, authenticate, create_user, normalize_email

router = APIRouter(prefix="/auth", tags=["auth"])

EMAIL_TAKEN = "An account with this email already exists"


def _set_session_cookie(response: Response, user_id: int, settings: Settings) -> None:
    response.set_cookie(
        ACCESS_TOKEN_COOKIE,
        create_access_token(str(user_id), settings),
        max_age=settings.access_token_ttl_minutes * 60,
        httponly=True,
        secure=settings.cookie_secure,
        samesite="lax",
    )


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(
    payload: RegisterRequest,
    response: Response,
    *,
    session: SessionDep,
    settings: SettingsDep,
    limiter: RateLimiterDep,
    client: ClientAddress,
) -> UserRead:
    """Create an account and sign it in. Limited per client address."""
    limiter.hit(Check(REGISTER_PER_CLIENT, ("register", client)))
    try:
        user = create_user(session, email=payload.email, password=payload.password)
    except UserAlreadyExistsError as error:
        raise HTTPException(status.HTTP_409_CONFLICT, detail=EMAIL_TAKEN) from error
    # A concurrent registration with the same email fails on the unique constraint.
    commit_or_conflict(session, EMAIL_TAKEN)
    _set_session_cookie(response, user.id, settings)
    return UserRead.model_validate(user)


@router.post("/login", status_code=status.HTTP_204_NO_CONTENT)
def login(
    credentials: LoginRequest,
    response: Response,
    *,
    session: SessionDep,
    settings: SettingsDep,
    limiter: RateLimiterDep,
    client: ClientAddress,
) -> None:
    """Sign in. Attempts are limited per client address and email, and per email."""
    email = normalize_email(credentials.email)
    limiter.hit(
        Check(LOGIN_PER_CLIENT_AND_EMAIL, ("login", client, email)),
        Check(LOGIN_PER_EMAIL, ("login", email)),
    )
    user = authenticate(session, email=credentials.email, password=credentials.password)
    if user is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    _set_session_cookie(response, user.id, settings)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(response: Response, settings: SettingsDep) -> None:
    response.delete_cookie(ACCESS_TOKEN_COOKIE, httponly=True, secure=settings.cookie_secure, samesite="lax")


@router.get("/me")
def read_current_user(user: CurrentUser) -> UserRead:
    return UserRead.model_validate(user)
