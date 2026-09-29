"""Password hashing (Argon2) and signed access tokens (JWT)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

import jwt
from pwdlib import PasswordHash

from gym_tracker.config import Settings

_password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    return _password_hash.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return _password_hash.verify(password, password_hash)


@dataclass(frozen=True)
class AccessToken:
    subject: str
    issued_at: datetime
    remember: bool


def token_ttl(settings: Settings, *, remember: bool) -> timedelta:
    """A remembered session lasts a week (renewed while in use); any other, half a day at most."""
    minutes = settings.access_token_ttl_minutes if remember else settings.session_token_ttl_minutes
    return timedelta(minutes=minutes)


def create_access_token(
    subject: str, settings: Settings, *, remember: bool = False, now: datetime | None = None
) -> str:
    issued_at = now or datetime.now(UTC)
    payload = {
        "sub": subject,
        "iat": issued_at,
        "exp": issued_at + token_ttl(settings, remember=remember),
        "remember": remember,
    }
    return jwt.encode(payload, settings.jwt_secret.get_secret_value(), algorithm=settings.jwt_algorithm)


def decode_access_token(token: str, settings: Settings) -> AccessToken | None:
    """Return the token's contents, or ``None`` when the token is invalid or expired."""
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret.get_secret_value(),
            algorithms=[settings.jwt_algorithm],
            options={"require": ["sub", "exp", "iat"]},
        )
    except jwt.InvalidTokenError:
        return None
    subject = payload["sub"]
    if not isinstance(subject, str):
        return None
    return AccessToken(
        subject=subject,
        issued_at=datetime.fromtimestamp(payload["iat"], UTC),
        # Tokens issued before this claim existed were all week-long sessions.
        remember=payload.get("remember", True) is True,
    )


def needs_renewal(token: AccessToken, settings: Settings, *, now: datetime | None = None) -> bool:
    """A remembered session is reissued once a day while in use, so it only ends after a week unused."""
    age = (now or datetime.now(UTC)) - token.issued_at
    return token.remember and age >= timedelta(minutes=settings.token_renewal_after_minutes)
