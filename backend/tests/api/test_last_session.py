from datetime import UTC, datetime
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from gym_tracker.models import Workout, WorkoutSet
from gym_tracker.users import create_user
from tests.api.conftest import catalog_exercise_id

pytestmark = pytest.mark.usefixtures("catalog")


def log_workout(client: TestClient, started_at: str, sets: list[dict[str, object]]) -> int:
    response = client.post("/api/workouts", json={"started_at": started_at, "sets": sets})
    assert response.status_code == 201
    return int(response.json()["id"])


def test_last_session_is_null_without_history(auth_client: TestClient, session: Session) -> None:
    pulldown = catalog_exercise_id(session, "lat-pulldown")

    response = auth_client.get(f"/api/exercises/{pulldown}/last-session")

    assert response.status_code == 200
    assert response.json() is None


def test_last_session_returns_latest_sets_for_the_exercise(auth_client: TestClient, session: Session) -> None:
    pulldown = catalog_exercise_id(session, "lat-pulldown")
    curl = catalog_exercise_id(session, "cable-curl")
    log_workout(
        auth_client,
        "2026-09-08T18:00:00+02:00",
        [{"exercise_id": pulldown, "set_number": 1, "reps": 8, "weight_kg": 50}],
    )
    latest = log_workout(
        auth_client,
        "2026-09-15T18:00:00+02:00",
        [
            {"exercise_id": pulldown, "set_number": 2, "reps": 9, "weight_kg": 52.5},
            {"exercise_id": curl, "set_number": 1, "reps": 12, "weight_kg": 20},
            {"exercise_id": pulldown, "set_number": 1, "reps": 10, "weight_kg": 52.5},
        ],
    )
    log_workout(
        auth_client,
        "2026-09-16T18:00:00+02:00",
        [{"exercise_id": curl, "set_number": 1, "reps": 12, "weight_kg": 22.5}],
    )

    last_session = auth_client.get(f"/api/exercises/{pulldown}/last-session").json()

    assert last_session["workout_id"] == latest
    assert [(s["set_number"], s["reps"], s["weight_kg"]) for s in last_session["sets"]] == [(1, 10, 52.5), (2, 9, 52.5)]


def test_last_session_ignores_other_users(auth_client: TestClient, session: Session) -> None:
    pulldown = catalog_exercise_id(session, "lat-pulldown")
    other = create_user(session, email="other@example.com", password="another-password")
    session.add(
        Workout(
            user_id=other.id,
            started_at=datetime(2026, 9, 15, 16, tzinfo=UTC),
            sets=[WorkoutSet(exercise_id=pulldown, set_number=1, reps=5, weight_kg=Decimal("100"))],
        )
    )
    session.flush()

    assert auth_client.get(f"/api/exercises/{pulldown}/last-session").json() is None


def test_last_session_of_unknown_exercise_is_not_found(auth_client: TestClient) -> None:
    assert auth_client.get("/api/exercises/999999/last-session").status_code == 404
