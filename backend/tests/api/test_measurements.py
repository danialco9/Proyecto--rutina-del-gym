from datetime import date
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from gym_tracker.models import BodyMeasurement
from gym_tracker.users import create_user


def dates(client: TestClient, **params: str) -> list[str]:
    return [measurement["measured_on"] for measurement in client.get("/api/measurements", params=params).json()]


def test_measurement_lifecycle(auth_client: TestClient) -> None:
    first = auth_client.post("/api/measurements", json={"measured_on": "2026-09-15", "weight_kg": 78.4, "waist_cm": 82})
    assert first.status_code == 201
    assert auth_client.post("/api/measurements", json={"measured_on": "2026-09-08", "weight_kg": 79}).status_code == 201

    assert dates(auth_client) == ["2026-09-08", "2026-09-15"]
    assert dates(auth_client, date_from="2026-09-10") == ["2026-09-15"]
    assert dates(auth_client, date_to="2026-09-10") == ["2026-09-08"]

    measurement_id = first.json()["id"]
    replaced = auth_client.put(
        f"/api/measurements/{measurement_id}", json={"measured_on": "2026-09-15", "weight_kg": 78.2}
    )
    assert replaced.status_code == 200
    assert replaced.json()["weight_kg"] == 78.2
    assert replaced.json()["waist_cm"] is None

    assert auth_client.delete(f"/api/measurements/{measurement_id}").status_code == 204
    assert dates(auth_client) == ["2026-09-08"]


def test_one_measurement_per_day(auth_client: TestClient) -> None:
    payload = {"measured_on": "2026-09-15", "weight_kg": 78.4}

    assert auth_client.post("/api/measurements", json=payload).status_code == 201
    assert auth_client.post("/api/measurements", json=payload).status_code == 409


@pytest.mark.parametrize(
    "payload",
    [
        {"measured_on": "2026-09-15"},
        {"measured_on": "2026-09-15", "body_fat_pct": 120},
        {"measured_on": "2026-09-15", "weight_kg": 0},
    ],
)
def test_rejects_invalid_measurements(auth_client: TestClient, payload: dict[str, object]) -> None:
    assert auth_client.post("/api/measurements", json=payload).status_code == 422


def test_measurements_of_other_users_are_hidden(auth_client: TestClient, session: Session) -> None:
    other = create_user(session, email="other@example.com", password="another-password")
    measurement = BodyMeasurement(user_id=other.id, measured_on=date(2026, 9, 15), weight_kg=Decimal("70"))
    session.add(measurement)
    session.flush()

    assert dates(auth_client) == []
    payload = {"measured_on": "2026-09-15", "weight_kg": 71}
    assert auth_client.put(f"/api/measurements/{measurement.id}", json=payload).status_code == 404
    assert auth_client.delete(f"/api/measurements/{measurement.id}").status_code == 404
