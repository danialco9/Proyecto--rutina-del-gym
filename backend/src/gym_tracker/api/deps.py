"""Shared FastAPI dependencies."""

from __future__ import annotations

from typing import Annotated

from fastapi import Cookie, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from gym_tracker.config import Settings, get_settings
from gym_tracker.db import get_session
from gym_tracker.mail import Mailer, get_mailer
from gym_tracker.models import User
from gym_tracker.rate_limit import RateLimiter
from gym_tracker.security import decode_access_token

ACCESS_TOKEN_COOKIE = "access_token"

SessionDep = Annotated[Session, Depends(get_session)]
SettingsDep = Annotated[Settings, Depends(get_settings)]


def get_current_user(
    session: SessionDep,
    settings: SettingsDep,
    access_token: Annotated[str | None, Cookie()] = None,
) -> User:
    unauthorized = HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    subject = decode_access_token(access_token, settings) if access_token else None
    if subject is None or not subject.isdigit():
        raise unauthorized
    user = session.get(User, int(subject))
    if user is None:
        raise unauthorized
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def get_rate_limiter(request: Request) -> RateLimiter:
    limiter: RateLimiter = request.app.state.rate_limiter
    return limiter


RateLimiterDep = Annotated[RateLimiter, Depends(get_rate_limiter)]


def get_app_mailer(settings: SettingsDep) -> Mailer:
    return get_mailer(settings)


MailerDep = Annotated[Mailer, Depends(get_app_mailer)]


def get_client_address(request: Request) -> str:
    """The caller's IP. Behind a reverse proxy, run uvicorn with ``--proxy-headers`` so this is the real client."""
    return request.client.host if request.client else "unknown"


ClientAddress = Annotated[str, Depends(get_client_address)]
