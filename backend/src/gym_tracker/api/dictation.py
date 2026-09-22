"""Reads a workout written in plain language and returns it for the user to review."""

from __future__ import annotations

from fastapi import APIRouter
from sqlalchemy import select

from gym_tracker.api.common import visible_to
from gym_tracker.api.deps import ClientAddress, CurrentUser, RateLimiterDep, SessionDep
from gym_tracker.dictation import ExerciseOption, get_reader
from gym_tracker.models import Exercise
from gym_tracker.rate_limit import DICTATION_PER_CLIENT, Check
from gym_tracker.schemas import (
    DictationExerciseRead,
    DictationIn,
    DictationRead,
    DictationSetRead,
    DictationSuggestion,
)

router = APIRouter(prefix="/dictation", tags=["dictation"])


@router.post("")
def read_workout(
    payload: DictationIn,
    *,
    session: SessionDep,
    user: CurrentUser,
    limiter: RateLimiterDep,
    client: ClientAddress,
) -> DictationRead:
    """Turn "prensa 4x10 120" into sets. Nothing is saved: the app prefills the workout screen with this.

    Reading is capped per caller. It is cheap today, but the reader is the seam a language model
    plugs into, and by then an unbounded endpoint would be somebody else's bill.
    """
    limiter.hit(Check(DICTATION_PER_CLIENT, ("dictation", client)))
    catalog = [
        ExerciseOption(id=exercise.id, name=exercise.name)
        for exercise in session.scalars(select(Exercise).where(visible_to(user)).order_by(Exercise.name, Exercise.id))
    ]
    return DictationRead(
        exercises=[
            DictationExerciseRead(
                query=item.query,
                name=item.name,
                exercise_id=item.exercise_id,
                sets=[
                    DictationSetRead(reps=item_set.reps, weight_kg=item_set.weight_kg, rpe=item_set.rpe)
                    for item_set in item.sets
                ],
                suggestions=[DictationSuggestion(id=option.id, name=option.name) for option in item.suggestions],
            )
            for item in get_reader().read(payload.text, catalog)
        ]
    )
