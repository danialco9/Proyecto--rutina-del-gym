import pytest
from fastapi.testclient import TestClient
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from gym_tracker.catalog import CATALOG, seed_catalog
from gym_tracker.models import Exercise
from tests.api.conftest import catalog_exercise_id

pytestmark = pytest.mark.usefixtures("catalog")

CUSTOM_EXERCISE = {"name": "Remo Gironda en máquina", "muscle_group": "back", "equipment": "machine"}


def test_exercises_require_authentication(client: TestClient) -> None:
    assert client.get("/api/exercises").status_code == 401


def test_list_filters_by_muscle_group(auth_client: TestClient) -> None:
    response = auth_client.get("/api/exercises", params={"muscle_group": "quads"})

    assert response.status_code == 200
    exercises = response.json()
    assert "Prensa de piernas" in [exercise["name"] for exercise in exercises]
    assert {exercise["muscle_group"] for exercise in exercises} == {"quads"}
    assert not any(exercise["is_custom"] for exercise in exercises)


def test_search_by_name(auth_client: TestClient) -> None:
    response = auth_client.get("/api/exercises", params={"q": "jalón"})

    assert {exercise["slug"] for exercise in response.json()} == {"lat-pulldown", "close-grip-lat-pulldown"}


def test_seed_catalog_is_idempotent(session: Session) -> None:
    seed_catalog(session)

    count = session.scalar(select(func.count()).select_from(Exercise).where(Exercise.user_id.is_(None)))
    assert count == len(CATALOG)


def test_custom_exercise_lifecycle(auth_client: TestClient) -> None:
    created = auth_client.post("/api/exercises", json=CUSTOM_EXERCISE)
    assert created.status_code == 201
    exercise = created.json()
    assert exercise["slug"] == "remo-gironda-en-maquina"
    assert exercise["is_custom"] is True

    updated = auth_client.patch(f"/api/exercises/{exercise['id']}", json={"secondary_muscles": ["biceps"]})
    assert updated.status_code == 200
    assert updated.json()["secondary_muscles"] == ["biceps"]
    assert updated.json()["name"] == CUSTOM_EXERCISE["name"]

    assert auth_client.delete(f"/api/exercises/{exercise['id']}").status_code == 204
    assert auth_client.get(f"/api/exercises/{exercise['id']}").status_code == 404


def test_duplicate_custom_slug_conflicts(auth_client: TestClient) -> None:
    assert auth_client.post("/api/exercises", json=CUSTOM_EXERCISE).status_code == 201
    assert auth_client.post("/api/exercises", json=CUSTOM_EXERCISE).status_code == 409


def test_catalog_exercises_are_read_only(auth_client: TestClient, session: Session) -> None:
    bench_press = catalog_exercise_id(session, "bench-press")

    assert auth_client.patch(f"/api/exercises/{bench_press}", json={"name": "Otro"}).status_code == 403
    assert auth_client.delete(f"/api/exercises/{bench_press}").status_code == 403


@pytest.mark.parametrize(
    "payload",
    [
        {"name": "Vuelo", "muscle_group": "wings"},
        {"name": "   ", "muscle_group": "abs"},
        {"name": "Crunch raro", "muscle_group": "abs", "slug": "Not A Slug"},
    ],
)
def test_create_validates_payload(auth_client: TestClient, payload: dict[str, str]) -> None:
    assert auth_client.post("/api/exercises", json=payload).status_code == 422


def test_patch_rejects_null_required_field(auth_client: TestClient) -> None:
    exercise_id = auth_client.post("/api/exercises", json=CUSTOM_EXERCISE).json()["id"]

    assert auth_client.patch(f"/api/exercises/{exercise_id}", json={"name": None}).status_code == 422


def test_exercise_in_use_cannot_be_deleted(auth_client: TestClient) -> None:
    exercise_id = auth_client.post("/api/exercises", json=CUSTOM_EXERCISE).json()["id"]
    routine = {"name": "Espalda", "exercises": [{"exercise_id": exercise_id}]}
    assert auth_client.post("/api/routines", json=routine).status_code == 201

    assert auth_client.delete(f"/api/exercises/{exercise_id}").status_code == 409
