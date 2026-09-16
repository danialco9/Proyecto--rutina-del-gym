from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from gym_tracker.config import Settings, get_settings
from gym_tracker.db import get_session
from gym_tracker.main import create_app
from gym_tracker.users import create_user

DEMO_EMAIL = "demo@example.com"


def demo_client(session: Session, settings: Settings, **overrides: object) -> TestClient:
    configured = settings.model_copy(update={"demo_email": DEMO_EMAIL, **overrides})
    app = create_app(configured)
    app.dependency_overrides[get_session] = lambda: session
    app.dependency_overrides[get_settings] = lambda: configured
    return TestClient(app)


@pytest.fixture
def enabled(session: Session, settings: Settings) -> Iterator[TestClient]:
    with demo_client(session, settings, demo_enabled=True) as client:
        yield client


def test_demo_signs_in_to_the_demo_account(enabled: TestClient, session: Session) -> None:
    create_user(session, email=DEMO_EMAIL, password="unknown-to-visitors")

    response = enabled.post("/api/auth/demo")

    assert response.status_code == 204
    assert "httponly" in response.headers["set-cookie"].lower()
    assert enabled.get("/api/auth/me").json()["email"] == DEMO_EMAIL


def test_demo_is_rate_limited_per_client(enabled: TestClient, session: Session) -> None:
    create_user(session, email=DEMO_EMAIL, password="unknown-to-visitors")

    statuses = [enabled.post("/api/auth/demo").status_code for _ in range(21)]

    assert statuses == [204] * 20 + [429]


def test_demo_is_unavailable_without_the_account(enabled: TestClient) -> None:
    assert enabled.post("/api/auth/demo").status_code == 404


def test_demo_is_disabled_by_default(session: Session, settings: Settings) -> None:
    create_user(session, email=DEMO_EMAIL, password="unknown-to-visitors")

    with demo_client(session, settings) as client:
        assert client.post("/api/auth/demo").status_code == 404


@pytest.mark.parametrize(
    "url",
    [
        "postgres://user:secret@db.example/app?sslmode=require",
        "postgresql://user:secret@db.example/app?sslmode=require",
    ],
)
def test_hosted_database_urls_use_psycopg(settings: Settings, url: str) -> None:
    configured = Settings.model_validate({**settings.model_dump(), "database_url": url})

    assert configured.database_url == "postgresql+psycopg://user:secret@db.example/app?sslmode=require"
