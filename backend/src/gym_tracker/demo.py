"""Realistic demo account: routines, a few months of simulated training and weigh-ins.

Each lift has a hidden strength level that grows a little every session (one of them stops
growing, so it stalls). Sessions are simulated set by set against that level, and the weight for the next
session is chosen with the same progression rules the app recommends, so the charts and the
recommendations look like a real training log.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from datetime import UTC, date, datetime, time, timedelta

import pandas as pd
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from gym_tracker.analysis import ProgressionRules, decide_progression, detect_plateaus
from gym_tracker.catalog import seed_catalog
from gym_tracker.models import BodyMeasurement, Exercise, Routine, RoutineExercise, User, Workout, WorkoutSet
from gym_tracker.users import create_user, normalize_email

DEMO_EMAIL = "demo@gymtracker.dev"
DEMO_PASSWORD = "demo-gym-tracker"

EPLEY_REPS_DIVISOR = 30.0
FATIGUE_PER_SET = 0.02
MIN_REPS = 3
EXTRA_REPS_OVER_TARGET = 2
SKIP_PROBABILITY = 0.08
WEIGH_IN_PROBABILITY = 0.75
SESSION_START_UTC = time(16, 30)
MONDAY, TUESDAY, WEDNESDAY, FRIDAY, SUNDAY = 0, 1, 2, 4, 6


@dataclass(frozen=True)
class DemoLift:
    slug: str
    target_sets: int
    target_reps: int
    start_weight_kg: float
    gain_per_session: float = 0.012
    stalls_after_week: int | None = None
    warmup: bool = False


ROUTINES: dict[str, tuple[DemoLift, ...]] = {
    "Torso A": (
        DemoLift("bench-press", 3, 8, 60, gain_per_session=0.012, warmup=True),
        DemoLift("lat-pulldown", 3, 10, 50),
        DemoLift("overhead-press", 3, 8, 37.5, stalls_after_week=5),
        DemoLift("seated-cable-row", 3, 10, 50),
        DemoLift("triceps-pushdown", 3, 12, 22.5),
    ),
    "Torso B": (
        DemoLift("incline-dumbbell-press", 3, 10, 22.5),
        DemoLift("machine-row", 3, 10, 55),
        DemoLift("barbell-curl", 3, 10, 25, gain_per_session=0.008),
        DemoLift("face-pull", 3, 15, 20, gain_per_session=0.006),
    ),
    "Pierna": (
        DemoLift("back-squat", 4, 6, 80, gain_per_session=0.015, warmup=True),
        DemoLift("romanian-deadlift", 3, 8, 70),
        DemoLift("leg-press", 3, 12, 140),
        DemoLift("lying-leg-curl", 3, 12, 35),
        DemoLift("standing-calf-raise", 4, 12, 60, gain_per_session=0.005),
    ),
}

ROUTINE_DESCRIPTIONS = {
    "Torso A": "Alterna con Torso B",
    "Torso B": "Alterna con Torso A",
    "Pierna": "Miércoles",
}


@dataclass
class _LiftState:
    lift: DemoLift
    capacity_kg: float
    weight_kg: float
    history: list[tuple[float, float]]  # (best e1RM, top weight) per session


@dataclass(frozen=True)
class DemoSummary:
    user: User
    workouts: int
    measurements: int


def _round_to(value: float, increment: float) -> float:
    return math.floor(value / increment) * increment


def _estimate_1rm(weight_kg: float, reps: int) -> float:
    return weight_kg * (1 + reps / EPLEY_REPS_DIVISOR) if reps > 1 else weight_kg


def _simulate_sets(state: _LiftState, week: int, rng: random.Random, rules: ProgressionRules) -> list[WorkoutSet]:
    """Perform one session of a lift and update the weight for the next one."""
    lift = state.lift
    if lift.stalls_after_week is None or week < lift.stalls_after_week:
        state.capacity_kg *= 1 + lift.gain_per_session * rng.uniform(0.3, 1.2)
    day_form = state.capacity_kg * rng.uniform(0.97, 1.03)

    sets: list[WorkoutSet] = []
    if lift.warmup:
        warmup_weight = _round_to(state.weight_kg * 0.5, rules.load_increment_kg)
        sets.append(WorkoutSet(set_number=1, reps=8, weight_kg=warmup_weight, rpe=None, is_warmup=True))

    reps_done: list[int] = []
    rpes: list[float] = []
    for index in range(lift.target_sets):
        available = day_form * (1 - FATIGUE_PER_SET * index)
        max_reps = max(MIN_REPS, math.floor(EPLEY_REPS_DIVISOR * (available / state.weight_kg - 1)))
        # Stop 1-2 reps short of failure, a little past the target at most.
        reps = max(MIN_REPS, min(max_reps - rng.choice((1, 2, 2, 3)), lift.target_reps + EXTRA_REPS_OVER_TARGET))
        rpe = min(10.0, max(6.0, round((10 - (max_reps - reps)) * 2) / 2))
        reps_done.append(reps)
        rpes.append(rpe)
        sets.append(WorkoutSet(set_number=len(sets) + 1, reps=reps, weight_kg=state.weight_kg, rpe=rpe))

    state.history.append((max(_estimate_1rm(state.weight_kg, reps) for reps in reps_done), state.weight_kg))
    bests = pd.DataFrame(
        {
            "exercise_id": lift.slug,
            "date": range(len(state.history)),
            "best_e1rm_kg": [best for best, _ in state.history],
            "top_weight_kg": [weight for _, weight in state.history],
        }
    )
    plateaus = detect_plateaus(bests, window=rules.plateau_window)
    stalled = bool(plateaus["stalled"].any())
    _, next_weight = decide_progression(
        top_weight_kg=state.weight_kg,
        reps=reps_done,
        max_rpe=max(rpes),
        target_sets=lift.target_sets,
        target_reps=lift.target_reps,
        stalled=stalled,
        rules=rules,
    )
    state.weight_kg = next_weight
    return sets


def _training_days(start: date, end: date) -> list[tuple[date, str]]:
    """Legs on Wednesday; Torso A and B alternate on Monday, Tuesday and Friday."""
    schedule: list[tuple[date, str]] = []
    upper = ("Torso A", "Torso B")
    upper_index = 0
    day = start
    while day < end:
        if day.weekday() == WEDNESDAY:
            schedule.append((day, "Pierna"))
        elif day.weekday() in {MONDAY, TUESDAY, FRIDAY}:
            schedule.append((day, upper[upper_index % 2]))
            upper_index += 1
        day += timedelta(days=1)
    return schedule


def seed_demo(
    session: Session,
    *,
    email: str = DEMO_EMAIL,
    password: str = DEMO_PASSWORD,
    weeks: int = 12,
    today: date | None = None,
    seed: int = 7,
) -> DemoSummary:
    """Create (or recreate) the demo account with ``weeks`` of history ending yesterday."""
    rng = random.Random(seed)  # Deterministic, not for security.
    rules = ProgressionRules()
    end = today or date.today()
    start = end - timedelta(weeks=weeks)

    session.execute(delete(User).where(User.email == normalize_email(email)))
    seed_catalog(session)
    user = create_user(session, email=email, password=password)

    slugs = {lift.slug for lifts in ROUTINES.values() for lift in lifts}
    exercise_ids = dict(
        session.execute(select(Exercise.slug, Exercise.id).where(Exercise.slug.in_(slugs), Exercise.user_id.is_(None)))
        .tuples()
        .all()
    )

    routines: dict[str, Routine] = {}
    states: dict[str, _LiftState] = {}
    for name, lifts in ROUTINES.items():
        routine = Routine(user_id=user.id, name=name, description=ROUTINE_DESCRIPTIONS[name])
        for position, lift in enumerate(lifts, start=1):
            routine.exercises.append(
                RoutineExercise(
                    exercise_id=exercise_ids[lift.slug],
                    position=position,
                    target_sets=lift.target_sets,
                    target_reps=lift.target_reps,
                )
            )
            capacity = lift.start_weight_kg * (1 + (lift.target_reps + 2) / EPLEY_REPS_DIVISOR)
            states[lift.slug] = _LiftState(lift, capacity, lift.start_weight_kg, history=[])
        routines[name] = routine
        session.add(routine)
    session.flush()

    workouts = 0
    for day, routine_name in _training_days(start, end):
        if rng.random() < SKIP_PROBABILITY:
            continue
        week = (day - start).days // 7
        started_at = datetime.combine(day, SESSION_START_UTC, tzinfo=UTC) + timedelta(minutes=rng.randint(-45, 60))
        workout = Workout(
            user_id=user.id,
            routine_id=routines[routine_name].id,
            started_at=started_at,
            ended_at=started_at + timedelta(minutes=rng.randint(55, 80)),
        )
        for lift in ROUTINES[routine_name]:
            for workout_set in _simulate_sets(states[lift.slug], week, rng, rules):
                workout_set.exercise_id = exercise_ids[lift.slug]
                workout.sets.append(workout_set)
        session.add(workout)
        workouts += 1

    measurements = 0
    for offset in range((end - start).days):
        day = start + timedelta(days=offset)
        if rng.random() > WEIGH_IN_PROBABILITY:
            continue
        weeks_in = offset / 7
        session.add(
            BodyMeasurement(
                user_id=user.id,
                measured_on=day,
                weight_kg=round(82.0 - 0.2 * weeks_in + rng.gauss(0, 0.35), 1),
                waist_cm=round(88.0 - 0.15 * weeks_in, 1) if day.weekday() == SUNDAY else None,
            )
        )
        measurements += 1

    session.flush()
    return DemoSummary(user=user, workouts=workouts, measurements=measurements)
