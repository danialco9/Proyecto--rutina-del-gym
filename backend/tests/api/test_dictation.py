import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from tests.api.conftest import catalog_exercise_id

pytestmark = pytest.mark.usefixtures("catalog")


def test_reads_a_dictation_against_the_user_catalog(auth_client: TestClient, session: Session) -> None:
    response = auth_client.post("/api/dictation", json={"text": "prensa 4x10 120\ndominadas 3x8"})

    assert response.status_code == 200
    exercises = response.json()["exercises"]
    assert [exercise["exercise_id"] for exercise in exercises] == [
        catalog_exercise_id(session, "leg-press"),
        catalog_exercise_id(session, "pull-up"),
    ]
    assert [len(exercise["sets"]) for exercise in exercises] == [4, 3]
    assert exercises[0]["sets"][0] == {"reps": 10, "weight_kg": 120.0, "rpe": None}


def test_an_unknown_exercise_comes_back_without_an_id(auth_client: TestClient) -> None:
    response = auth_client.post("/api/dictation", json={"text": "maquina rarisima 3x10"})

    exercise = response.json()["exercises"][0]
    assert exercise["exercise_id"] is None
    assert exercise["name"] == "maquina rarisima"


def test_reading_saves_nothing(auth_client: TestClient) -> None:
    auth_client.post("/api/dictation", json={"text": "prensa 4x10 120"})

    assert auth_client.get("/api/workouts").json() == []


def test_empty_text_is_rejected(auth_client: TestClient) -> None:
    assert auth_client.post("/api/dictation", json={"text": "  "}).status_code == 422


def test_requires_a_session(client: TestClient) -> None:
    assert client.post("/api/dictation", json={"text": "prensa 4x10"}).status_code == 401
