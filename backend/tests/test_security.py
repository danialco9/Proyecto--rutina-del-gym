from datetime import UTC, datetime, timedelta

import jwt
import pytest
from pydantic import SecretStr

from gym_tracker.config import Settings
from gym_tracker.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    needs_renewal,
    verify_password,
)

SETTINGS = Settings(
    database_url="postgresql+psycopg://unused@localhost/unused",
    jwt_secret=SecretStr("test-secret-that-is-at-least-32-bytes-long"),
    access_token_ttl_minutes=15,
    token_renewal_after_minutes=5,
    session_token_ttl_minutes=10,
)


def test_password_hash_roundtrip() -> None:
    password_hash = hash_password("s3cret-password")

    assert password_hash.startswith("$argon2")
    assert verify_password("s3cret-password", password_hash)
    assert not verify_password("other-password", password_hash)


@pytest.mark.parametrize("remember", [True, False])
def test_access_token_roundtrip(remember: bool) -> None:
    token = decode_access_token(create_access_token("42", SETTINGS, remember=remember), SETTINGS)

    assert token is not None
    assert token.subject == "42"
    assert token.remember is remember


@pytest.mark.parametrize(
    ("remember", "minutes_ago", "valid"), [(True, 14, True), (True, 16, False), (False, 11, False)]
)
def test_remembered_tokens_last_longer(remember: bool, minutes_ago: int, valid: bool) -> None:
    issued = datetime.now(UTC) - timedelta(minutes=minutes_ago)
    token = create_access_token("42", SETTINGS, remember=remember, now=issued)

    assert (decode_access_token(token, SETTINGS) is not None) is valid


def test_token_signed_with_other_secret_is_rejected() -> None:
    other = SETTINGS.model_copy(update={"jwt_secret": SecretStr("another-secret-that-is-32-bytes-long!")})

    assert decode_access_token(create_access_token("42", other), SETTINGS) is None


def test_tokens_from_before_the_remember_claim_count_as_remembered() -> None:
    now = datetime.now(UTC)
    legacy = jwt.encode(
        {"sub": "42", "iat": now, "exp": now + timedelta(minutes=5)},
        SETTINGS.jwt_secret.get_secret_value(),
        algorithm=SETTINGS.jwt_algorithm,
    )

    token = decode_access_token(legacy, SETTINGS)
    assert token is not None
    assert token.remember is True


@pytest.mark.parametrize(("remember", "minutes_ago", "renew"), [(True, 4, False), (True, 6, True), (False, 6, False)])
def test_only_remembered_sessions_are_renewed_once_old_enough(remember: bool, minutes_ago: int, renew: bool) -> None:
    now = datetime.now(UTC)
    raw = create_access_token("42", SETTINGS, remember=remember, now=now - timedelta(minutes=minutes_ago))
    token = decode_access_token(raw, SETTINGS)

    assert token is not None
    assert needs_renewal(token, SETTINGS, now=now) is renew
