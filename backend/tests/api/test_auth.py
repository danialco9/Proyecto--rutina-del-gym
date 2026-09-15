import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from gym_tracker.models import User
from gym_tracker.users import UserAlreadyExistsError, create_user
from tests.api.conftest import TEST_EMAIL, TEST_PASSWORD


def login(client: TestClient, email: str = TEST_EMAIL, password: str = TEST_PASSWORD) -> int:
    response = client.post("/api/auth/login", json={"email": email, "password": password})
    return int(response.status_code)


@pytest.mark.usefixtures("user")
def test_login_sets_http_only_cookie_and_authenticates(client: TestClient) -> None:
    response = client.post("/api/auth/login", json={"email": "Dani@Example.com", "password": TEST_PASSWORD})

    assert response.status_code == 204
    cookie = response.headers["set-cookie"]
    assert cookie.startswith("access_token=")
    assert "HttpOnly" in cookie
    assert "SameSite=lax" in cookie

    me = client.get("/api/auth/me")
    assert me.status_code == 200
    assert me.json()["email"] == TEST_EMAIL


@pytest.mark.usefixtures("user")
@pytest.mark.parametrize(
    ("email", "password"),
    [(TEST_EMAIL, "wrong-password"), ("nobody@example.com", TEST_PASSWORD)],
)
def test_login_rejects_invalid_credentials(client: TestClient, email: str, password: str) -> None:
    response = client.post("/api/auth/login", json={"email": email, "password": password})

    assert response.status_code == 401
    assert "set-cookie" not in response.headers


def test_me_requires_authentication(client: TestClient) -> None:
    assert client.get("/api/auth/me").status_code == 401


def test_me_rejects_tampered_token(client: TestClient) -> None:
    client.cookies.set("access_token", "not-a-valid-token")

    assert client.get("/api/auth/me").status_code == 401


@pytest.mark.usefixtures("user")
def test_logout_clears_session(client: TestClient) -> None:
    assert login(client) == 204

    assert client.post("/api/auth/logout").status_code == 204
    assert client.get("/api/auth/me").status_code == 401


def test_create_user_rejects_duplicates_and_short_passwords(session: Session, user: User) -> None:
    with pytest.raises(UserAlreadyExistsError):
        create_user(session, email=user.email.upper(), password=TEST_PASSWORD)
    with pytest.raises(ValueError, match="at least"):
        create_user(session, email="other@example.com", password="short")
