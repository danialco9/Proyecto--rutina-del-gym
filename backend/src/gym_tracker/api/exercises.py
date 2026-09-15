"""Exercise catalog and custom exercises."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from gym_tracker.api.common import commit_or_conflict, escape_like, not_found, visible_to
from gym_tracker.api.deps import CurrentUser, SessionDep
from gym_tracker.enums import MuscleGroup
from gym_tracker.models import Exercise, User
from gym_tracker.schemas import ExerciseCreate, ExerciseRead, ExerciseUpdate
from gym_tracker.slugs import slugify

router = APIRouter(prefix="/exercises", tags=["exercises"])

DUPLICATE_SLUG = "An exercise with this slug already exists"


def _get_visible(session: Session, exercise_id: int, user: User) -> Exercise:
    exercise = session.scalar(select(Exercise).where(Exercise.id == exercise_id, visible_to(user)))
    if exercise is None:
        raise not_found("Exercise")
    return exercise


def _get_editable(session: Session, exercise_id: int, user: User) -> Exercise:
    exercise = _get_visible(session, exercise_id, user)
    if not exercise.is_custom:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="Catalog exercises cannot be modified")
    return exercise


@router.get("")
def list_exercises(
    session: SessionDep,
    user: CurrentUser,
    muscle_group: MuscleGroup | None = None,
    q: Annotated[str | None, Query(max_length=100)] = None,
) -> list[ExerciseRead]:
    query = select(Exercise).where(visible_to(user)).order_by(Exercise.name, Exercise.id)
    if muscle_group is not None:
        query = query.where(Exercise.muscle_group == muscle_group.value)
    if q:
        query = query.where(Exercise.name.ilike(f"%{escape_like(q)}%", escape="\\"))
    return [ExerciseRead.model_validate(exercise) for exercise in session.scalars(query)]


@router.get("/{exercise_id}")
def read_exercise(exercise_id: int, session: SessionDep, user: CurrentUser) -> ExerciseRead:
    return ExerciseRead.model_validate(_get_visible(session, exercise_id, user))


@router.post("", status_code=status.HTTP_201_CREATED)
def create_exercise(payload: ExerciseCreate, session: SessionDep, user: CurrentUser) -> ExerciseRead:
    exercise = Exercise(
        user_id=user.id,
        slug=payload.slug or slugify(payload.name),
        name=payload.name,
        muscle_group=payload.muscle_group,
        secondary_muscles=list(payload.secondary_muscles),
        equipment=payload.equipment,
    )
    session.add(exercise)
    commit_or_conflict(session, DUPLICATE_SLUG)
    return ExerciseRead.model_validate(exercise)


@router.patch("/{exercise_id}")
def update_exercise(exercise_id: int, payload: ExerciseUpdate, session: SessionDep, user: CurrentUser) -> ExerciseRead:
    exercise = _get_editable(session, exercise_id, user)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(exercise, field, value)
    commit_or_conflict(session, DUPLICATE_SLUG)
    return ExerciseRead.model_validate(exercise)


@router.delete("/{exercise_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_exercise(exercise_id: int, session: SessionDep, user: CurrentUser) -> None:
    session.delete(_get_editable(session, exercise_id, user))
    commit_or_conflict(session, "Exercise is used by a routine or workout")
