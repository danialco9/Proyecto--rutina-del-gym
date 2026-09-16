from collections.abc import Iterator
from datetime import UTC, date, datetime
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from gym_tracker.api.progress import get_today
from gym_tracker.models import Workout, WorkoutSet
from gym_tracker.users import create_user
from tests.api.conftest import catalog_exercise_id

pytestmark = pytest.mark.usefixtures("catalog")

TODAY = date(2026, 9, 16)


@pytest.fixture
def progress_client(auth_client: TestClient) -> Iterator[TestClient]:
    auth_client.app.dependency_overrides[get_today] = lambda: TODAY  # type: ignore[attr-defined]
    yield auth_client
    auth_client.app.dependency_overrides.pop(get_today)  # type: ignore[attr-defined]


def post(client: TestClient, path: str, payload: dict[str, object]) -> dict[str, object]:
    response = client.post(path, json=payload)
    assert response.status_code == 201, response.text
    body: dict[str, object] = response.json()
    return body


def bench_set(bench: int, set_number: int, reps: int, weight: float, rpe: float | None = None) -> dict[str, object]:
    return {"exercise_id": bench, "set_number": set_number, "reps": reps, "weight_kg": weight, "rpe": rpe}


@pytest.fixture
def training_log(progress_client: TestClient, session: Session) -> dict[str, int]:
    """Two upper-body sessions a week apart and three weigh-ins."""
    bench = catalog_exercise_id(session, "bench-press")
    pulldown = catalog_exercise_id(session, "lat-pulldown")
    routine = post(
        progress_client,
        "/api/routines",
        {"name": "Torso", "exercises": [{"exercise_id": bench, "target_sets": 3, "target_reps": 8}]},
    )
    post(
        progress_client,
        "/api/workouts",
        {
            "routine_id": routine["id"],
            "started_at": "2026-09-08T18:00:00+02:00",
            "sets": [
                {**bench_set(bench, 1, 10, 40), "is_warmup": True},
                *(bench_set(bench, number, 8, 60, 8) for number in (2, 3, 4)),
            ],
        },
    )
    post(
        progress_client,
        "/api/workouts",
        {
            "routine_id": routine["id"],
            "started_at": "2026-09-15T18:00:00+02:00",
            "sets": [
                *(bench_set(bench, number, 8, 62.5, 7.5) for number in (1, 2, 3)),
                *(bench_set(pulldown, number, 10, 50, 9) for number in (1, 2)),
            ],
        },
    )
    for measured_on, weight in (("2026-09-10", 80.0), ("2026-09-14", 79.6), ("2026-09-15", 79.4)):
        post(progress_client, "/api/measurements", {"measured_on": measured_on, "weight_kg": weight})
    post(progress_client, "/api/measurements", {"measured_on": "2026-09-16", "waist_cm": 82})
    return {"bench": bench, "pulldown": pulldown}


def test_overview_without_data(progress_client: TestClient) -> None:
    overview = progress_client.get("/api/progress/overview").json()

    assert overview["activity"] == {
        "workouts_total": 0,
        "workouts_last_7_days": 0,
        "workouts_last_28_days": 0,
        "last_workout_on": None,
    }
    assert overview["recommendations"] == []
    assert overview["personal_records"] == []
    assert [week["week_start"] for week in overview["weekly_volume"]] == [
        "2026-07-27",
        "2026-08-03",
        "2026-08-10",
        "2026-08-17",
        "2026-08-24",
        "2026-08-31",
        "2026-09-07",
        "2026-09-14",
    ]
    assert all(week["muscles"] == [] for week in overview["weekly_volume"])
    assert overview["body_weight"] == {"entries": [], "weekly_change_kg": None}


def test_overview_summarizes_the_training_log(progress_client: TestClient, training_log: dict[str, int]) -> None:
    overview = progress_client.get("/api/progress/overview").json()

    assert overview["activity"] == {
        "workouts_total": 2,
        "workouts_last_7_days": 1,
        "workouts_last_28_days": 2,
        "last_workout_on": "2026-09-15",
    }
    assert overview["recommendations"] == [
        {
            "exercise_id": training_log["bench"],
            "exercise_name": "Press banca con barra",
            "action": "increase_load",
            "last_performed_on": "2026-09-15",
            "last_weight_kg": 62.5,
            "last_reps": [8, 8, 8],
            "target_reps": 8,
            "suggested_weight_kg": 65.0,
        },
        {
            "exercise_id": training_log["pulldown"],
            "exercise_name": "Jalón al pecho",
            "action": "increase_reps",
            "last_performed_on": "2026-09-15",
            "last_weight_kg": 50.0,
            "last_reps": [10, 10],
            "target_reps": None,
            "suggested_weight_kg": 50.0,
        },
    ]
    assert overview["personal_records"] == [
        {
            "exercise_id": training_log["pulldown"],
            "exercise_name": "Jalón al pecho",
            "muscle_group": "back",
            "sessions": 1,
            "best_e1rm_kg": 66.7,
            "best_e1rm_on": "2026-09-15",
            "max_weight_kg": 50.0,
            "max_weight_on": "2026-09-15",
        },
        {
            "exercise_id": training_log["bench"],
            "exercise_name": "Press banca con barra",
            "muscle_group": "chest",
            "sessions": 2,
            "best_e1rm_kg": 79.2,
            "best_e1rm_on": "2026-09-15",
            "max_weight_kg": 62.5,
            "max_weight_on": "2026-09-15",
        },
    ]
    # The warm-up set is not a hard set.
    assert overview["weekly_volume"][-2:] == [
        {"week_start": "2026-09-07", "muscles": [{"muscle_group": "chest", "hard_sets": 3, "volume_kg": 1440.0}]},
        {
            "week_start": "2026-09-14",
            "muscles": [
                {"muscle_group": "back", "hard_sets": 2, "volume_kg": 1000.0},
                {"muscle_group": "chest", "hard_sets": 3, "volume_kg": 1500.0},
            ],
        },
    ]
    assert overview["body_weight"] == {
        "entries": [
            {"measured_on": "2026-09-10", "weight_kg": 80.0, "trend_kg": 80.0},
            {"measured_on": "2026-09-14", "weight_kg": 79.6, "trend_kg": 79.8},
            {"measured_on": "2026-09-15", "weight_kg": 79.4, "trend_kg": 79.67},
        ],
        "weekly_change_kg": -0.8,
    }


def test_exercise_progress_lists_sessions(progress_client: TestClient, training_log: dict[str, int]) -> None:
    response = progress_client.get(f"/api/progress/exercises/{training_log['bench']}")

    assert response.status_code == 200
    assert response.json() == {
        "exercise_id": training_log["bench"],
        "exercise_name": "Press banca con barra",
        "sessions": [
            {
                "workout_id": response.json()["sessions"][0]["workout_id"],
                "performed_on": "2026-09-08",
                "best_e1rm_kg": 76.0,
                "top_weight_kg": 60.0,
                "working_sets": 3,
                "total_reps": 24,
                "volume_kg": 1440.0,
            },
            {
                "workout_id": response.json()["sessions"][1]["workout_id"],
                "performed_on": "2026-09-15",
                "best_e1rm_kg": 79.2,
                "top_weight_kg": 62.5,
                "working_sets": 3,
                "total_reps": 24,
                "volume_kg": 1500.0,
            },
        ],
    }


def test_progress_ignores_other_users(progress_client: TestClient, session: Session) -> None:
    squat = catalog_exercise_id(session, "back-squat")
    other = create_user(session, email="other@example.com", password="another-password")
    session.add(
        Workout(
            user_id=other.id,
            started_at=datetime(2026, 9, 15, 16, tzinfo=UTC),
            sets=[WorkoutSet(exercise_id=squat, set_number=1, reps=5, weight_kg=Decimal("100"))],
        )
    )
    session.flush()

    assert progress_client.get("/api/progress/overview").json()["activity"]["workouts_total"] == 0
    assert progress_client.get(f"/api/progress/exercises/{squat}").json()["sessions"] == []


def test_exercise_progress_of_unknown_exercise_is_not_found(progress_client: TestClient) -> None:
    assert progress_client.get("/api/progress/exercises/999999").status_code == 404


def test_progress_requires_authentication(client: TestClient) -> None:
    assert client.get("/api/progress/overview").status_code == 401
