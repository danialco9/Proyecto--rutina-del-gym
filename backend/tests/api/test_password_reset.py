import json
from datetime import UTC, datetime, timedelta

import httpx
import pytest
from fastapi.testclient import TestClient
from pydantic import SecretStr
from sqlalchemy.orm import Session

from gym_tracker.api.deps import get_app_mailer
from gym_tracker.config import Settings
from gym_tracker.demo import DEMO_EMAIL
from gym_tracker.mail import BREVO_SEND_URL, BrevoMailer, Email, LogMailer, get_mailer
from gym_tracker.models import User
from gym_tracker.password_reset import create_reset_token
from gym_tracker.users import create_user
from tests.api.conftest import TEST_EMAIL, TEST_PASSWORD

NEW_PASSWORD = "a-brand-new-password"


class RecordingMailer:
    def __init__(self) -> None:
        self.sent: list[Email] = []

    def send(self, email: Email) -> None:
        self.sent.append(email)

    def token(self) -> str:
        """The token in the link of the last email, as the reset page reads it."""
        link = next(word for word in self.sent[-1].text.split() if "/restablecer#token=" in word)
        return link.split("#token=", 1)[1]


class BrokenMailer:
    def send(self, email: Email) -> None:
        raise httpx.ConnectError("Brevo is down")


@pytest.fixture
def mailer(client: TestClient) -> RecordingMailer:
    recording = RecordingMailer()
    client.app.dependency_overrides[get_app_mailer] = lambda: recording  # type: ignore[attr-defined]
    return recording


def ask_for_link(client: TestClient, email: str = TEST_EMAIL) -> int:
    return int(client.post("/api/auth/password-reset", json={"email": email}).status_code)


def choose_password(client: TestClient, token: str, password: str = NEW_PASSWORD) -> int:
    response = client.post("/api/auth/password-reset/confirm", json={"token": token, "password": password})
    return int(response.status_code)


def login(client: TestClient, password: str) -> int:
    return int(client.post("/api/auth/login", json={"email": TEST_EMAIL, "password": password}).status_code)


@pytest.mark.usefixtures("user")
def test_the_emailed_link_sets_a_new_password(client: TestClient, mailer: RecordingMailer) -> None:
    assert ask_for_link(client, TEST_EMAIL.upper()) == 204

    [email] = mailer.sent
    assert email.to == TEST_EMAIL
    assert "http://localhost:5173/restablecer#token=" in email.text
    assert "30 minutos" in email.text

    assert choose_password(client, mailer.token()) == 204
    assert login(client, NEW_PASSWORD) == 204
    assert login(client, TEST_PASSWORD) == 401


def test_unknown_emails_get_the_same_answer_and_no_email(client: TestClient, mailer: RecordingMailer) -> None:
    assert ask_for_link(client, "nobody@example.com") == 204
    assert mailer.sent == []


def test_the_demo_account_gets_no_email(client: TestClient, session: Session, mailer: RecordingMailer) -> None:
    create_user(session, email=DEMO_EMAIL, password=TEST_PASSWORD)

    assert ask_for_link(client, DEMO_EMAIL) == 204
    assert mailer.sent == []


@pytest.mark.usefixtures("user")
def test_a_link_works_once_and_using_one_cancels_the_others(client: TestClient, mailer: RecordingMailer) -> None:
    ask_for_link(client)
    first = mailer.token()
    ask_for_link(client)
    second = mailer.token()

    assert choose_password(client, second) == 204
    assert choose_password(client, second, "another-new-password") == 400
    assert choose_password(client, first, "another-new-password") == 400
    assert login(client, NEW_PASSWORD) == 204


def test_an_expired_link_is_refused(client: TestClient, session: Session, user: User) -> None:
    long_ago = datetime.now(UTC) - timedelta(hours=2)
    token = create_reset_token(session, user, now=long_ago, ttl=timedelta(minutes=30))

    assert choose_password(client, token) == 400
    assert login(client, TEST_PASSWORD) == 204


@pytest.mark.usefixtures("user")
def test_rejects_made_up_links_and_short_passwords(client: TestClient, mailer: RecordingMailer) -> None:
    assert choose_password(client, "made-up-token") == 400

    ask_for_link(client)
    assert choose_password(client, mailer.token(), "short") == 422


@pytest.mark.usefixtures("user", "mailer")
def test_each_inbox_gets_at_most_three_emails_an_hour(client: TestClient) -> None:
    assert [ask_for_link(client) for _ in range(4)] == [204, 204, 204, 429]


@pytest.mark.usefixtures("user")
def test_a_failing_mail_service_does_not_change_the_answer(client: TestClient) -> None:
    client.app.dependency_overrides[get_app_mailer] = BrokenMailer  # type: ignore[attr-defined]

    assert ask_for_link(client) == 204


def test_brevo_receives_the_email_and_the_key() -> None:
    requests: list[httpx.Request] = []

    def brevo(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(201, json={"messageId": "<1@brevo>"})

    mailer = BrevoMailer(
        "secret-key", "me@example.com", "Gym Tracker", httpx.Client(transport=httpx.MockTransport(brevo))
    )
    mailer.send(Email(to="you@example.com", subject="Hola", text="Texto", html="<p>Texto</p>"))

    [request] = requests
    assert str(request.url) == BREVO_SEND_URL
    assert request.headers["api-key"] == "secret-key"
    assert json.loads(request.content) == {
        "sender": {"email": "me@example.com", "name": "Gym Tracker"},
        "to": [{"email": "you@example.com"}],
        "subject": "Hola",
        "textContent": "Texto",
        "htmlContent": "<p>Texto</p>",
    }


def test_without_a_brevo_key_emails_go_to_the_log(settings: Settings) -> None:
    assert isinstance(get_mailer(settings), LogMailer)
    configured = settings.model_copy(update={"brevo_api_key": SecretStr("key"), "mail_from": "me@example.com"})
    assert isinstance(get_mailer(configured), BrevoMailer)
