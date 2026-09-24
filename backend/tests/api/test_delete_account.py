import httpx
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from gym_tracker.demo import DEMO_EMAIL
from gym_tracker.models import BodyMeasurement, Exercise, Routine, User, Workout
from gym_tracker.users import create_user
from tests.api.conftest import TEST_EMAIL, TEST_PASSWORD, catalog_exercise_id

pytestmark = pytest.mark.usefixtures("catalog")

OTHER_EMAIL = "other@example.com"


def delete_account(client: TestClient, password: str = TEST_PASSWORD) -> httpx.Response:
    # httpx only takes a body on DELETE through the generic `request`.
    response: httpx.Response = client.request("DELETE", "/api/auth/me", json={"password": password})
    return response


def fill_account(client: TestClient, session: Session) -> None:
    """A bit of everything, including an own exercise used by both a routine and a workout."""
    own = client.post("/api/exercises", json={"name": "Remo Gironda en máquina", "muscle_group": "back"}).json()["id"]
    squat = catalog_exercise_id(session, "back-squat")
    client.post("/api/routines", json={"name": "Espalda", "exercises": [{"exercise_id": own, "sets": [{}]}]})
    sets = [{"exercise_id": exercise_id, "set_number": 1, "reps": 10, "weight_kg": 50} for exercise_id in (own, squat)]
    client.post("/api/workouts", json={"started_at": "2026-09-20T18:00:00+02:00", "sets": sets})
    client.post("/api/measurements", json={"measured_on": "2026-09-20", "weight_kg": 78})


def count_owned(session: Session, model: type[Exercise | Routine | Workout | BodyMeasurement], user_id: int) -> int:
    return session.scalar(select(func.count()).where(model.user_id == user_id)) or 0


def test_deletes_the_account_with_all_its_data(auth_client: TestClient, session: Session, user: User) -> None:
    fill_account(auth_client, session)
    user_id = user.id
    for model in (Exercise, Routine, Workout, BodyMeasurement):
        assert count_owned(session, model, user_id) == 1, model.__name__

    response = delete_account(auth_client)

    assert response.status_code == 204
    assert 'access_token=""' in response.headers["set-cookie"]
    assert session.get(User, user_id) is None
    for model in (Exercise, Routine, Workout, BodyMeasurement):
        assert count_owned(session, model, user_id) == 0, model.__name__
    assert auth_client.get("/api/auth/me").status_code == 401


def test_leaves_other_accounts_alone(auth_client: TestClient, session: Session, user: User) -> None:
    other = create_user(session, email=OTHER_EMAIL, password=TEST_PASSWORD)
    fill_account(auth_client, session)

    assert delete_account(auth_client).status_code == 204

    assert session.get(User, other.id) is not None
    assert catalog_exercise_id(session, "back-squat") > 0
    login = auth_client.post("/api/auth/login", json={"email": OTHER_EMAIL, "password": TEST_PASSWORD})
    assert login.status_code == 204


def test_a_wrong_password_keeps_the_account_and_the_session(auth_client: TestClient, user: User) -> None:
    response = delete_account(auth_client, password="not-my-password")

    assert response.status_code == 403
    assert "set-cookie" not in response.headers
    assert auth_client.get("/api/auth/me").json()["email"] == TEST_EMAIL


def test_requires_a_session(client: TestClient) -> None:
    assert delete_account(client).status_code == 401


def test_the_demo_account_cannot_be_deleted(client: TestClient, session: Session) -> None:
    create_user(session, email=DEMO_EMAIL, password=TEST_PASSWORD)
    client.post("/api/auth/login", json={"email": DEMO_EMAIL, "password": TEST_PASSWORD})

    assert delete_account(client).status_code == 403
    assert client.get("/api/auth/me").status_code == 200


@pytest.mark.usefixtures("user")
def test_password_attempts_share_the_login_limit(auth_client: TestClient) -> None:
    # The fixture's own login already used one of the five attempts a minute.
    statuses = [delete_account(auth_client, password="guess").status_code for _ in range(5)]

    assert statuses == [403, 403, 403, 403, 429]
