import pytest
from fastapi.testclient import TestClient

from tests.api.conftest import TEST_EMAIL


def test_register_creates_account_and_signs_in(client: TestClient) -> None:
    response = client.post("/api/auth/register", json={"email": "New@Example.com", "password": "a-strong-password"})

    assert response.status_code == 201
    assert response.json()["email"] == "new@example.com"
    assert "HttpOnly" in response.headers["set-cookie"]
    assert client.get("/api/auth/me").json()["email"] == "new@example.com"
    assert client.post("/api/auth/logout").status_code == 204
    login = client.post("/api/auth/login", json={"email": "new@example.com", "password": "a-strong-password"})
    assert login.status_code == 204


@pytest.mark.usefixtures("user")
def test_register_rejects_existing_email(client: TestClient) -> None:
    response = client.post("/api/auth/register", json={"email": TEST_EMAIL.upper(), "password": "a-strong-password"})

    assert response.status_code == 409
    assert "set-cookie" not in response.headers


@pytest.mark.parametrize(
    "payload",
    [
        {"email": "not-an-email", "password": "a-strong-password"},
        {"email": "short@example.com", "password": "short"},
    ],
)
def test_register_validates_payload(client: TestClient, payload: dict[str, str]) -> None:
    assert client.post("/api/auth/register", json=payload).status_code == 422
