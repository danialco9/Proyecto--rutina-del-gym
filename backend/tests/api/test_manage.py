import getpass
from collections.abc import Iterator
from contextlib import nullcontext

import pytest
from sqlalchemy.orm import Session

from gym_tracker import manage
from gym_tracker.models import User
from gym_tracker.users import UserNotFoundError, authenticate, set_password
from tests.api.conftest import TEST_EMAIL, TEST_PASSWORD

NEW_PASSWORD = "a-brand-new-password"


@pytest.fixture
def admin_session(monkeypatch: pytest.MonkeyPatch, session: Session) -> Session:
    """Makes the admin commands work on the test session instead of opening their own.

    `nullcontext` keeps the command's `with` block from closing it, which would roll back the
    test's own data along with the command's.
    """
    monkeypatch.setattr(manage, "get_sessionmaker", lambda: lambda: nullcontext(session))
    return session


def type_passwords(monkeypatch: pytest.MonkeyPatch, *answers: str) -> None:
    typed: Iterator[str] = iter(answers)
    monkeypatch.setattr(getpass, "getpass", lambda _prompt: next(typed))


def test_set_password_replaces_the_old_one(session: Session, user: User) -> None:
    set_password(session, email=user.email.upper(), password=NEW_PASSWORD)

    assert authenticate(session, email=TEST_EMAIL, password=NEW_PASSWORD) is not None
    assert authenticate(session, email=TEST_EMAIL, password=TEST_PASSWORD) is None


@pytest.mark.usefixtures("user")
def test_set_password_rejects_unknown_emails_and_short_passwords(session: Session) -> None:
    with pytest.raises(UserNotFoundError):
        set_password(session, email="nobody@example.com", password=NEW_PASSWORD)
    with pytest.raises(ValueError, match="at least"):
        set_password(session, email=TEST_EMAIL, password="short")


@pytest.mark.usefixtures("user")
def test_reset_password_command(
    monkeypatch: pytest.MonkeyPatch, admin_session: Session, capsys: pytest.CaptureFixture[str]
) -> None:
    type_passwords(monkeypatch, NEW_PASSWORD, NEW_PASSWORD)

    manage.main(["reset-password", "--email", TEST_EMAIL])

    assert f"Contraseña cambiada: {TEST_EMAIL}" in capsys.readouterr().out
    assert authenticate(admin_session, email=TEST_EMAIL, password=NEW_PASSWORD) is not None


@pytest.mark.usefixtures("user")
def test_reset_password_command_keeps_the_old_password_on_a_typo(
    monkeypatch: pytest.MonkeyPatch, admin_session: Session
) -> None:
    type_passwords(monkeypatch, NEW_PASSWORD, "a-brand-new-pasword")

    with pytest.raises(SystemExit):
        manage.main(["reset-password", "--email", TEST_EMAIL])

    assert authenticate(admin_session, email=TEST_EMAIL, password=TEST_PASSWORD) is not None


def test_reset_password_command_rejects_an_unknown_email(
    admin_session: Session, capsys: pytest.CaptureFixture[str]
) -> None:
    with pytest.raises(SystemExit):
        manage.main(["reset-password", "--email", "nobody@example.com"])

    assert "No existe ningún usuario" in capsys.readouterr().err
