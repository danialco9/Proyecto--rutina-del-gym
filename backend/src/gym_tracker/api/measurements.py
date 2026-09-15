"""Body weight and circumference measurements."""

from __future__ import annotations

from datetime import date

from fastapi import APIRouter, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from gym_tracker.api.common import commit_or_conflict, not_found
from gym_tracker.api.deps import CurrentUser, SessionDep
from gym_tracker.models import BodyMeasurement, User
from gym_tracker.schemas import BodyMeasurementIn, BodyMeasurementRead

router = APIRouter(prefix="/measurements", tags=["measurements"])

DUPLICATE_DATE = "A measurement for this date already exists"


def _get_measurement(session: Session, measurement_id: int, user: User) -> BodyMeasurement:
    measurement = session.get(BodyMeasurement, measurement_id)
    if measurement is None or measurement.user_id != user.id:
        raise not_found("Measurement")
    return measurement


@router.get("")
def list_measurements(
    session: SessionDep,
    user: CurrentUser,
    date_from: date | None = None,
    date_to: date | None = None,
) -> list[BodyMeasurementRead]:
    query = select(BodyMeasurement).where(BodyMeasurement.user_id == user.id).order_by(BodyMeasurement.measured_on)
    if date_from is not None:
        query = query.where(BodyMeasurement.measured_on >= date_from)
    if date_to is not None:
        query = query.where(BodyMeasurement.measured_on <= date_to)
    return [BodyMeasurementRead.model_validate(measurement) for measurement in session.scalars(query)]


@router.post("", status_code=status.HTTP_201_CREATED)
def create_measurement(payload: BodyMeasurementIn, session: SessionDep, user: CurrentUser) -> BodyMeasurementRead:
    measurement = BodyMeasurement(user_id=user.id, **payload.model_dump())
    session.add(measurement)
    commit_or_conflict(session, DUPLICATE_DATE)
    return BodyMeasurementRead.model_validate(measurement)


@router.put("/{measurement_id}")
def replace_measurement(
    measurement_id: int, payload: BodyMeasurementIn, session: SessionDep, user: CurrentUser
) -> BodyMeasurementRead:
    measurement = _get_measurement(session, measurement_id, user)
    for field, value in payload.model_dump().items():
        setattr(measurement, field, value)
    commit_or_conflict(session, DUPLICATE_DATE)
    return BodyMeasurementRead.model_validate(measurement)


@router.delete("/{measurement_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_measurement(measurement_id: int, session: SessionDep, user: CurrentUser) -> None:
    session.delete(_get_measurement(session, measurement_id, user))
    session.commit()
