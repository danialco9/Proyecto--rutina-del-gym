"""Training sessions and the sets performed in them."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from gym_tracker.api.common import UNPROCESSABLE, commit_or_conflict, ensure_exercises_visible, not_found
from gym_tracker.api.deps import CurrentUser, SessionDep
from gym_tracker.models import Routine, User, Workout, WorkoutSet
from gym_tracker.schemas import WorkoutIn, WorkoutRead, WorkoutSetIn, WorkoutSetRead

router = APIRouter(prefix="/workouts", tags=["workouts"])

DUPLICATE_SET = "Set number already used for this exercise in the workout"


def _get_workout(session: Session, workout_id: int, user: User) -> Workout:
    workout = session.scalar(
        select(Workout).where(Workout.id == workout_id, Workout.user_id == user.id).options(selectinload(Workout.sets))
    )
    if workout is None:
        raise not_found("Workout")
    return workout


def _validate_references(session: Session, user: User, payload: WorkoutIn) -> None:
    if payload.routine_id is not None:
        owned = select(Routine.id).where(Routine.id == payload.routine_id, Routine.user_id == user.id)
        if session.scalar(owned) is None:
            raise HTTPException(UNPROCESSABLE, detail="Unknown routine id")
    ensure_exercises_visible(session, user, (workout_set.exercise_id for workout_set in payload.sets))


def _sets(payload: WorkoutIn) -> list[WorkoutSet]:
    return [WorkoutSet(**workout_set.model_dump()) for workout_set in payload.sets]


@router.get("")
def list_workouts(
    session: SessionDep,
    user: CurrentUser,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> list[WorkoutRead]:
    query = (
        select(Workout)
        .where(Workout.user_id == user.id)
        .options(selectinload(Workout.sets))
        .order_by(Workout.started_at.desc(), Workout.id.desc())
        .limit(limit)
        .offset(offset)
    )
    return [WorkoutRead.model_validate(workout) for workout in session.scalars(query)]


@router.get("/{workout_id}")
def read_workout(workout_id: int, session: SessionDep, user: CurrentUser) -> WorkoutRead:
    return WorkoutRead.model_validate(_get_workout(session, workout_id, user))


@router.post("", status_code=status.HTTP_201_CREATED)
def create_workout(payload: WorkoutIn, session: SessionDep, user: CurrentUser) -> WorkoutRead:
    _validate_references(session, user, payload)
    workout = Workout(
        user_id=user.id,
        routine_id=payload.routine_id,
        started_at=payload.started_at,
        ended_at=payload.ended_at,
        notes=payload.notes,
        sets=_sets(payload),
    )
    session.add(workout)
    commit_or_conflict(session, DUPLICATE_SET)
    return WorkoutRead.model_validate(_get_workout(session, workout.id, user))


@router.put("/{workout_id}")
def replace_workout(workout_id: int, payload: WorkoutIn, session: SessionDep, user: CurrentUser) -> WorkoutRead:
    workout = _get_workout(session, workout_id, user)
    _validate_references(session, user, payload)
    # Delete the old sets first: set numbers are unique per exercise within a workout.
    workout.sets.clear()
    session.flush()
    workout.routine_id = payload.routine_id
    workout.started_at = payload.started_at
    workout.ended_at = payload.ended_at
    workout.notes = payload.notes
    workout.sets.extend(_sets(payload))
    commit_or_conflict(session, DUPLICATE_SET)
    return WorkoutRead.model_validate(_get_workout(session, workout.id, user))


@router.delete("/{workout_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_workout(workout_id: int, session: SessionDep, user: CurrentUser) -> None:
    session.delete(_get_workout(session, workout_id, user))
    session.commit()


@router.post("/{workout_id}/sets", status_code=status.HTTP_201_CREATED)
def add_set(workout_id: int, payload: WorkoutSetIn, session: SessionDep, user: CurrentUser) -> WorkoutSetRead:
    workout = _get_workout(session, workout_id, user)
    ensure_exercises_visible(session, user, [payload.exercise_id])
    workout_set = WorkoutSet(**payload.model_dump())
    workout.sets.append(workout_set)
    commit_or_conflict(session, DUPLICATE_SET)
    return WorkoutSetRead.model_validate(workout_set)


@router.delete("/{workout_id}/sets/{set_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_set(workout_id: int, set_id: int, session: SessionDep, user: CurrentUser) -> None:
    workout = _get_workout(session, workout_id, user)
    workout_set = next((item for item in workout.sets if item.id == set_id), None)
    if workout_set is None:
        raise not_found("Set")
    workout.sets.remove(workout_set)
    session.commit()
