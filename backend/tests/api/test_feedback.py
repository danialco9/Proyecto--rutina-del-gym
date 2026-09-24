from contextlib import nullcontext
from datetime import UTC, datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from gym_tracker import manage
from gym_tracker.config import Settings
from gym_tracker.models import Feedback, User
from tests.api.conftest import TEST_EMAIL, TEST_PASSWORD


def stored(session: Session) -> list[tuple[str, str | None]]:
    return [(item.message, item.page) for item in session.scalars(select(Feedback).order_by(Feedback.id))]


def test_stores_a_comment_with_the_screen_it_came_from(auth_client: TestClient, session: Session) -> None:
    response = auth_client.post("/api/feedback", json={"message": "  El temporizador no suena  ", "page": "/entrenar"})

    assert response.status_code == 204
    assert stored(session) == [("El temporizador no suena", "/entrenar")]


@pytest.mark.parametrize("message", ["", "   ", "x" * 2001])
def test_rejects_empty_and_huge_comments(auth_client: TestClient, session: Session, message: str) -> None:
    assert auth_client.post("/api/feedback", json={"message": message}).status_code == 422
    assert stored(session) == []


def test_requires_a_session(client: TestClient) -> None:
    assert client.post("/api/feedback", json={"message": "Hola"}).status_code == 401


def test_is_limited_per_account(auth_client: TestClient) -> None:
    statuses = [auth_client.post("/api/feedback", json={"message": f"#{n}"}).status_code for n in range(21)]

    assert statuses == [204] * 20 + [429]


def test_goes_with_the_account(auth_client: TestClient, session: Session) -> None:
    auth_client.post("/api/feedback", json={"message": "Me gusta"})

    deleted = auth_client.request("DELETE", "/api/auth/me", json={"password": TEST_PASSWORD})

    assert deleted.status_code == 204
    assert stored(session) == []


def test_admin_command_shows_the_latest_first_in_local_time(
    monkeypatch: pytest.MonkeyPatch,
    session: Session,
    settings: Settings,
    user: User,
    capsys: pytest.CaptureFixture[str],
) -> None:
    # `nullcontext` keeps the command from closing, and so rolling back, the test's session.
    monkeypatch.setattr(manage, "get_sessionmaker", lambda: lambda: nullcontext(session))
    monkeypatch.setattr(manage, "get_settings", lambda: settings)
    session.add_all(
        [
            Feedback(user_id=user.id, message="Primera", created_at=datetime(2026, 9, 24, 9, 0, tzinfo=UTC)),
            Feedback(user_id=user.id, message="Segunda", created_at=datetime(2026, 9, 24, 10, 42, tzinfo=UTC)),
        ]
    )
    session.flush()

    manage.main(["feedback", "--limit", "1"])

    out = capsys.readouterr().out
    assert f"2026-09-24 12:42 · {TEST_EMAIL} · -" in out  # Europe/Madrid, UTC+2 in September
    assert "Segunda" in out
    assert "Primera" not in out
