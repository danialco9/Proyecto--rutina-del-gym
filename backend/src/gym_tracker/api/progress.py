"""Progress analytics computed on demand from the user's training log."""

from __future__ import annotations

from datetime import date, timedelta
from typing import Annotated

import pandas as pd
from fastapi import APIRouter, Depends
from sqlalchemy import select

from gym_tracker.analysis import (
    TrainingLog,
    personal_records,
    recommend,
    session_bests,
    weekly_volume_by_muscle,
    weekly_weight_change,
    weight_trend,
    working_sets,
)
from gym_tracker.analysis.database import load_user_log
from gym_tracker.api.common import not_found, visible_to
from gym_tracker.api.deps import CurrentUser, SessionDep
from gym_tracker.models import Exercise
from gym_tracker.schemas import (
    ActivityRead,
    BodyWeightPointRead,
    BodyWeightRead,
    ExerciseProgressRead,
    ExerciseSessionRead,
    MuscleVolumeRead,
    PersonalRecordRead,
    ProgressOverviewRead,
    RecommendationRead,
    WeeklyVolumeRead,
)

router = APIRouter(prefix="/progress", tags=["progress"])

VOLUME_WEEKS = 8


def get_today() -> date:
    return date.today()


TodayDep = Annotated[date, Depends(get_today)]


def _activity(log: TrainingLog, today: date) -> ActivityRead:
    days = log.workouts["date"].dt.date
    return ActivityRead(
        workouts_total=len(days),
        workouts_last_7_days=int((days > today - timedelta(days=7)).sum()),
        workouts_last_28_days=int((days > today - timedelta(days=28)).sum()),
        last_workout_on=days.max() if len(days) else None,
    )


def _recommendations(log: TrainingLog, work: pd.DataFrame) -> list[RecommendationRead]:
    last_dates = work.groupby("exercise_id")["date"].max().dt.date
    return [
        RecommendationRead(
            exercise_id=int(item.exercise_id),
            exercise_name=item.exercise_name,
            action=item.action,
            last_performed_on=last_dates[item.exercise_id],
            last_weight_kg=item.last_weight_kg,
            last_reps=list(item.last_reps),
            target_reps=item.target_reps,
            suggested_weight_kg=item.suggested_weight_kg,
        )
        for item in recommend(log)
    ]


def _personal_records(log: TrainingLog, work: pd.DataFrame, bests: pd.DataFrame) -> list[PersonalRecordRead]:
    exercises = log.exercises.set_index("exercise_id")
    sessions = bests.groupby("exercise_id")["workout_id"].nunique()
    records = [
        PersonalRecordRead(
            exercise_id=int(record["exercise_id"]),
            exercise_name=str(exercises.at[record["exercise_id"], "name"]),
            muscle_group=str(exercises.at[record["exercise_id"], "muscle_group"]),
            sessions=int(sessions[record["exercise_id"]]),
            best_e1rm_kg=round(float(record["best_e1rm_kg"]), 1),
            best_e1rm_on=record["best_e1rm_date"].date(),
            max_weight_kg=float(record["max_weight_kg"]),
            max_weight_on=record["max_weight_date"].date(),
        )
        for record in personal_records(work).to_dict(orient="records")
    ]
    return sorted(records, key=lambda record: record.exercise_name)


def _weekly_volume(log: TrainingLog, work: pd.DataFrame, today: date) -> list[WeeklyVolumeRead]:
    """Hard sets per muscle for the current week and the previous ones, including empty weeks."""
    current_week = today - timedelta(days=today.weekday())
    weeks = [current_week - timedelta(weeks=offset) for offset in reversed(range(VOLUME_WEEKS))]
    volume = weekly_volume_by_muscle(work, log.exercises) if not work.empty else pd.DataFrame()
    by_week: dict[date, list[MuscleVolumeRead]] = {week: [] for week in weeks}
    for row in volume.to_dict(orient="records"):
        week = row["week_start"].date()
        if week in by_week:
            by_week[week].append(
                MuscleVolumeRead(
                    muscle_group=str(row["muscle_group"]),
                    hard_sets=int(row["hard_sets"]),
                    volume_kg=round(float(row["volume_kg"]), 1),
                )
            )
    return [WeeklyVolumeRead(week_start=week, muscles=muscles) for week, muscles in by_week.items()]


def _body_weight(log: TrainingLog) -> BodyWeightRead:
    trend = weight_trend(log.body_measurements)
    change = weekly_weight_change(log.body_measurements)
    return BodyWeightRead(
        entries=[
            BodyWeightPointRead(
                measured_on=row["date"].date(),
                weight_kg=float(row["weight_kg"]),
                trend_kg=round(float(row["trend_kg"]), 2),
            )
            for row in trend.to_dict(orient="records")
        ],
        weekly_change_kg=None if change is None else round(change, 2),
    )


@router.get("/overview")
def read_overview(session: SessionDep, user: CurrentUser, today: TodayDep) -> ProgressOverviewRead:
    """Activity, next-session recommendations, records, weekly volume and body weight trend."""
    log = load_user_log(session, user.id)
    work = working_sets(log)
    bests = session_bests(work)
    return ProgressOverviewRead(
        activity=_activity(log, today),
        recommendations=_recommendations(log, work) if not work.empty else [],
        personal_records=_personal_records(log, work, bests) if not work.empty else [],
        weekly_volume=_weekly_volume(log, work, today),
        body_weight=_body_weight(log),
    )


@router.get("/exercises/{exercise_id}")
def read_exercise_progress(exercise_id: int, session: SessionDep, user: CurrentUser) -> ExerciseProgressRead:
    """Best estimated 1RM, top weight and volume of every session that included the exercise."""
    name = session.scalar(select(Exercise.name).where(Exercise.id == exercise_id, visible_to(user)))
    if name is None:
        raise not_found("Exercise")
    work = working_sets(load_user_log(session, user.id))
    bests = session_bests(work[work["exercise_id"] == str(exercise_id)])
    return ExerciseProgressRead(
        exercise_id=exercise_id,
        exercise_name=name,
        sessions=[
            ExerciseSessionRead(
                workout_id=int(row["workout_id"]),
                performed_on=row["date"].date(),
                best_e1rm_kg=round(float(row["best_e1rm_kg"]), 1),
                top_weight_kg=float(row["top_weight_kg"]),
                working_sets=int(row["working_sets"]),
                total_reps=int(row["total_reps"]),
                volume_kg=round(float(row["volume_kg"]), 1),
            )
            for row in bests.to_dict(orient="records")
        ],
    )
