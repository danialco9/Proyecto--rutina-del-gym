import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from gym_tracker.models import Routine
from gym_tracker.users import create_user
from tests.api.conftest import catalog_exercise_id

pytestmark = pytest.mark.usefixtures("catalog")


def leg_day(session: Session) -> dict[str, object]:
    return {
        "name": "Pierna",
        "description": "Miércoles",
        "exercises": [
            {
                "exercise_id": catalog_exercise_id(session, "back-squat"),
                "target_sets": 4,
                "target_reps": 8,
                "target_weight_kg": 60,
            },
            {
                "exercise_id": catalog_exercise_id(session, "leg-press"),
                "target_sets": 4,
                "target_reps": 12,
                "target_rpe": 8,
            },
        ],
    }


def test_create_and_list_routine(auth_client: TestClient, session: Session) -> None:
    response = auth_client.post("/api/routines", json=leg_day(session))

    assert response.status_code == 201
    routine = response.json()
    assert [item["position"] for item in routine["exercises"]] == [1, 2]
    assert routine["exercises"][0]["exercise"]["slug"] == "back-squat"
    assert routine["exercises"][0]["target_weight_kg"] == 60.0
    assert routine["exercises"][1]["target_rpe"] == 8.0
    assert [item["name"] for item in auth_client.get("/api/routines").json()] == ["Pierna"]


def test_replace_routine_exercises(auth_client: TestClient, session: Session) -> None:
    routine_id = auth_client.post("/api/routines", json=leg_day(session)).json()["id"]
    payload = {
        "name": "Pierna A",
        "exercises": [{"exercise_id": catalog_exercise_id(session, "leg-extension"), "target_sets": 3}],
    }

    response = auth_client.put(f"/api/routines/{routine_id}", json=payload)

    assert response.status_code == 200
    routine = response.json()
    assert routine["name"] == "Pierna A"
    assert routine["description"] is None
    assert [(item["position"], item["exercise"]["slug"]) for item in routine["exercises"]] == [(1, "leg-extension")]


def test_duplicate_routine_name_conflicts(auth_client: TestClient, session: Session) -> None:
    assert auth_client.post("/api/routines", json=leg_day(session)).status_code == 201
    assert auth_client.post("/api/routines", json=leg_day(session)).status_code == 409


def test_unknown_exercise_is_rejected(auth_client: TestClient) -> None:
    payload = {"name": "Fantasma", "exercises": [{"exercise_id": 999_999}]}

    assert auth_client.post("/api/routines", json=payload).status_code == 422


def test_routines_of_other_users_are_hidden(auth_client: TestClient, session: Session) -> None:
    other = create_user(session, email="other@example.com", password="another-password")
    routine = Routine(user_id=other.id, name="Ajena")
    session.add(routine)
    session.flush()

    assert auth_client.get("/api/routines").json() == []
    assert auth_client.get(f"/api/routines/{routine.id}").status_code == 404
    assert auth_client.delete(f"/api/routines/{routine.id}").status_code == 404


def test_delete_routine(auth_client: TestClient, session: Session) -> None:
    routine_id = auth_client.post("/api/routines", json=leg_day(session)).json()["id"]

    assert auth_client.delete(f"/api/routines/{routine_id}").status_code == 204
    assert auth_client.get(f"/api/routines/{routine_id}").status_code == 404
