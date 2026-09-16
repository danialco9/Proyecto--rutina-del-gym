from datetime import UTC, datetime, timedelta

from pydantic import SecretStr

from gym_tracker.config import Settings
from gym_tracker.security import create_access_token, decode_access_token, hash_password, verify_password

SETTINGS = Settings(
    database_url="postgresql+psycopg://unused@localhost/unused",
    jwt_secret=SecretStr("test-secret-that-is-at-least-32-bytes-long"),
    access_token_ttl_minutes=15,
)


def test_password_hash_roundtrip() -> None:
    password_hash = hash_password("s3cret-password")

    assert password_hash.startswith("$argon2")
    assert verify_password("s3cret-password", password_hash)
    assert not verify_password("other-password", password_hash)


def test_access_token_roundtrip() -> None:
    assert decode_access_token(create_access_token("42", SETTINGS), SETTINGS) == "42"


def test_expired_token_is_rejected() -> None:
    token = create_access_token("42", SETTINGS, now=datetime.now(UTC) - timedelta(minutes=16))

    assert decode_access_token(token, SETTINGS) is None


def test_token_signed_with_other_secret_is_rejected() -> None:
    other = SETTINGS.model_copy(update={"jwt_secret": SecretStr("another-secret-that-is-32-bytes-long!")})

    assert decode_access_token(create_access_token("42", other), SETTINGS) is None
