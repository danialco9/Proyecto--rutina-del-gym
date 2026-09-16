from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from gym_tracker.api.deps import get_client_address
from gym_tracker.config import Settings, get_settings
from gym_tracker.db import get_session
from gym_tracker.main import create_app
from gym_tracker.models import User
from tests.api.conftest import TEST_PASSWORD


def login(client: TestClient, email: str, password: str = "wrong-password") -> int:
    status_code: int = client.post("/api/auth/login", json={"email": email, "password": password}).status_code
    return status_code


def from_address(client: TestClient, address: str) -> None:
    client.app.dependency_overrides[get_client_address] = lambda: address  # type: ignore[attr-defined]


def test_login_is_limited_per_client_and_email(client: TestClient, user: User) -> None:
    assert [login(client, user.email) for _ in range(5)] == [401] * 5

    blocked = client.post("/api/auth/login", json={"email": user.email, "password": TEST_PASSWORD})

    assert blocked.status_code == 429
    assert blocked.json() == {"detail": "Too many attempts, try again later"}
    assert 1 <= int(blocked.headers["Retry-After"]) <= 60
    # The same address can still sign in to another account, and the email matches case-insensitively.
    assert login(client, "someone@example.com") == 401
    assert login(client, user.email.upper()) == 429


def test_login_is_limited_per_email_across_addresses(client: TestClient, user: User) -> None:
    for attempt in range(20):
        from_address(client, f"203.0.113.{attempt}")
        assert login(client, user.email) == 401

    from_address(client, "198.51.100.1")

    assert login(client, user.email, TEST_PASSWORD) == 429


def test_registration_is_limited_per_client(client: TestClient) -> None:
    def register(number: int) -> int:
        account = {"email": f"new{number}@example.com", "password": "a-long-password"}
        status_code: int = client.post("/api/auth/register", json=account).status_code
        return status_code

    assert [register(number) for number in range(5)] == [201] * 5
    assert register(5) == 429

    from_address(client, "198.51.100.7")
    assert register(6) == 201


@pytest.fixture
def unlimited_client(session: Session, settings: Settings) -> Iterator[TestClient]:
    unlimited = settings.model_copy(update={"rate_limit_enabled": False})
    app = create_app(unlimited)
    app.dependency_overrides[get_session] = lambda: session
    app.dependency_overrides[get_settings] = lambda: unlimited
    with TestClient(app) as test_client:
        yield test_client


def test_limits_can_be_disabled(unlimited_client: TestClient, user: User) -> None:
    assert {login(unlimited_client, user.email) for _ in range(8)} == {401}
