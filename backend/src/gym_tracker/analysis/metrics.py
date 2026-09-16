"""Performance and body composition metrics computed from the training log."""

from __future__ import annotations

import numpy as np
import pandas as pd

from gym_tracker.analysis.loader import TrainingLog

EPLEY_REPS_DIVISOR = 30.0
MIN_DATES_FOR_TREND = 2


def estimate_1rm(weight_kg: pd.Series, reps: pd.Series) -> pd.Series:
    """Estimate the one-rep max with the Epley formula (a single rep is its own max)."""
    return (weight_kg * (1 + reps / EPLEY_REPS_DIVISOR)).where(reps > 1, weight_kg)


def working_sets(log: TrainingLog) -> pd.DataFrame:
    """Non-warm-up sets with at least one rep, joined with the workout date.

    Adds ``e1rm_kg`` (estimated one-rep max) and ``volume_kg`` (weight x reps).
    Rows are sorted chronologically so ties resolve to the earliest occurrence.
    """
    sets = log.workout_sets
    mask = ~sets["is_warmup"] & (sets["reps"] >= 1)
    work = sets.loc[mask].merge(
        log.workouts[["workout_id", "date", "routine_id"]],
        on="workout_id",
        how="inner",
        validate="many_to_one",
    )
    work = work.sort_values(["date", "workout_id", "set_number"], ignore_index=True)
    return work.assign(
        e1rm_kg=estimate_1rm(work["weight_kg"], work["reps"]),
        volume_kg=work["weight_kg"] * work["reps"],
    )


def session_bests(work: pd.DataFrame) -> pd.DataFrame:
    """Summarize each exercise per workout: best e1RM, top weight, sets, reps and volume."""
    return (
        work.groupby(["exercise_id", "workout_id", "date"], as_index=False)
        .agg(
            best_e1rm_kg=("e1rm_kg", "max"),
            top_weight_kg=("weight_kg", "max"),
            working_sets=("reps", "count"),
            total_reps=("reps", "sum"),
            volume_kg=("volume_kg", "sum"),
        )
        .sort_values(["exercise_id", "date"], ignore_index=True)
    )


def personal_records(work: pd.DataFrame) -> pd.DataFrame:
    """Best estimated 1RM and heaviest weight per exercise, with the date achieved."""
    columns = ["exercise_id", "best_e1rm_kg", "best_e1rm_date", "max_weight_kg", "max_weight_date"]
    if work.empty:
        return pd.DataFrame(columns=columns)

    by_exercise = work.groupby("exercise_id")
    best_e1rm = work.loc[by_exercise["e1rm_kg"].idxmax(), ["exercise_id", "e1rm_kg", "date"]].rename(
        columns={"e1rm_kg": "best_e1rm_kg", "date": "best_e1rm_date"}
    )
    heaviest = work.loc[by_exercise["weight_kg"].idxmax(), ["exercise_id", "weight_kg", "date"]].rename(
        columns={"weight_kg": "max_weight_kg", "date": "max_weight_date"}
    )
    return best_e1rm.merge(heaviest, on="exercise_id").sort_values("exercise_id", ignore_index=True)[columns]


def weekly_volume_by_muscle(work: pd.DataFrame, exercises: pd.DataFrame) -> pd.DataFrame:
    """Hard sets and tonnage per primary muscle group per week (weeks start on Monday)."""
    return (
        work.merge(exercises[["exercise_id", "muscle_group"]], on="exercise_id", how="left", validate="many_to_one")
        .assign(
            week_start=lambda d: d["date"].dt.to_period("W-SUN").dt.start_time,
            muscle_group=lambda d: d["muscle_group"].fillna("unknown"),
        )
        .groupby(["week_start", "muscle_group"], as_index=False)
        .agg(hard_sets=("reps", "count"), volume_kg=("volume_kg", "sum"))
        .sort_values(["week_start", "muscle_group"], ignore_index=True)
    )


def weight_trend(body: pd.DataFrame, window_days: int = 7) -> pd.DataFrame:
    """Body weight with a time-based rolling mean (``trend_kg``) to smooth daily noise."""
    weights = body.dropna(subset=["weight_kg"]).sort_values("date", ignore_index=True)[["date", "weight_kg"]]
    trend = weights.set_index("date")["weight_kg"].rolling(f"{window_days}D").mean()
    return weights.assign(trend_kg=trend.to_numpy())


def weekly_weight_change(body: pd.DataFrame, lookback_days: int = 28) -> float | None:
    """Body weight change in kg per week, from a linear fit over the recent lookback window."""
    weights = body.dropna(subset=["weight_kg"])
    if weights.empty:
        return None
    recent = weights[weights["date"] >= weights["date"].max() - pd.Timedelta(days=lookback_days)]
    if recent["date"].nunique() < MIN_DATES_FOR_TREND:
        return None
    days = (recent["date"] - recent["date"].min()).dt.days.to_numpy(dtype=float)
    slope_per_day = np.polyfit(days, recent["weight_kg"].to_numpy(dtype=float), 1)[0]
    return float(slope_per_day * 7)


def detect_plateaus(bests: pd.DataFrame, window: int = 3, min_improvement: float = 0.01) -> pd.DataFrame:
    """Flag exercises whose last ``window`` sessions did not beat the previous best e1RM.

    An exercise counts as stalled when its best recent e1RM is below the earlier best
    improved by ``min_improvement`` (1% by default). Needs more than ``window`` sessions.
    """
    columns = ["exercise_id", "previous_best_kg", "recent_best_kg", "stalled"]
    rows = []
    for exercise_id, group in bests.sort_values("date").groupby("exercise_id"):
        if len(group) <= window:
            continue
        history = group["best_e1rm_kg"].to_numpy(dtype=float)
        previous_best = float(history[:-window].max())
        recent_best = float(history[-window:].max())
        rows.append(
            {
                "exercise_id": exercise_id,
                "previous_best_kg": previous_best,
                "recent_best_kg": recent_best,
                "stalled": recent_best < previous_best * (1 + min_improvement),
            }
        )
    return pd.DataFrame(rows, columns=columns)
