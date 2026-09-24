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
from gym_tracker.rate_limit import (
    DEMO_PER_CLIENT,
    LOGIN_PER_CLIENT_AND_EMAIL,
    LOGIN_PER_EMAIL,
    REGISTER_PER_CLIENT,
    Check,
)
from gym_tracker.schemas import DeleteAccountRequest, LoginRequest, RegisterRequest, UserRead
from gym_tracker.security import create_access_token, verify_password
from gym_tracker.users import (
    UserAlreadyExistsError,
    authenticate,
    create_user,
    delete_user,
    get_user_by_email,
    normalize_email,
)

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


@router.post("/demo", status_code=status.HTTP_204_NO_CONTENT)
def demo_login(
    response: Response,
    *,
    session: SessionDep,
    settings: SettingsDep,
    limiter: RateLimiterDep,
    client: ClientAddress,
) -> None:
    """Sign in to the public demo account without a password, when the demo is enabled."""
    user = get_user_by_email(session, settings.demo_email) if settings.demo_enabled else None
    if user is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Demo not available")
    limiter.hit(Check(DEMO_PER_CLIENT, ("demo", client)))
    _set_session_cookie(response, user.id, settings)


def _clear_session_cookie(response: Response, settings: Settings) -> None:
    response.delete_cookie(ACCESS_TOKEN_COOKIE, httponly=True, secure=settings.cookie_secure, samesite="lax")


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(response: Response, settings: SettingsDep) -> None:
    _clear_session_cookie(response, settings)


@router.get("/me")
def read_current_user(user: CurrentUser) -> UserRead:
    return UserRead.model_validate(user)


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
def delete_account(
    payload: DeleteAccountRequest,
    response: Response,
    *,
    user: CurrentUser,
    session: SessionDep,
    settings: SettingsDep,
    limiter: RateLimiterDep,
    client: ClientAddress,
) -> None:
    """Delete the signed-in account and all its data, after confirming the password.

    A wrong password answers 403, not 401: the session is still valid. Attempts count against the
    same limits as logging in, so this is no side door for guessing passwords.
    """
    if user.email == normalize_email(settings.demo_email):
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="The demo account cannot be deleted")
    limiter.hit(
        Check(LOGIN_PER_CLIENT_AND_EMAIL, ("login", client, user.email)),
        Check(LOGIN_PER_EMAIL, ("login", user.email)),
    )
    if not verify_password(payload.password, user.password_hash):
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="Incorrect password")
    delete_user(session, user)
    session.commit()
    _clear_session_cookie(response, settings)
