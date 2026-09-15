"""Per-exercise training history, used to show the last performance while logging."""

from __future__ import annotations

from fastapi import APIRouter
from sqlalchemy import select

from gym_tracker.api.common import not_found, visible_to
from gym_tracker.api.deps import CurrentUser, SessionDep
from gym_tracker.models import Exercise, Workout, WorkoutSet
from gym_tracker.schemas import LastSessionRead, WorkoutSetRead

router = APIRouter(prefix="/exercises", tags=["exercises"])


@router.get("/{exercise_id}/last-session")
def read_last_session(exercise_id: int, session: SessionDep, user: CurrentUser) -> LastSessionRead | None:
    """Sets from the most recent workout that included the exercise, or ``null`` if never trained."""
    if session.scalar(select(Exercise.id).where(Exercise.id == exercise_id, visible_to(user))) is None:
        raise not_found("Exercise")
    workout = session.scalar(
        select(Workout)
        .join(Workout.sets)
        .where(Workout.user_id == user.id, WorkoutSet.exercise_id == exercise_id)
        .order_by(Workout.started_at.desc(), Workout.id.desc())
        .limit(1)
    )
    if workout is None:
        return None
    sets = session.scalars(
        select(WorkoutSet)
        .where(WorkoutSet.workout_id == workout.id, WorkoutSet.exercise_id == exercise_id)
        .order_by(WorkoutSet.set_number)
    )
    return LastSessionRead(
        workout_id=workout.id,
        started_at=workout.started_at,
        sets=[WorkoutSetRead.model_validate(workout_set) for workout_set in sets],
    )
