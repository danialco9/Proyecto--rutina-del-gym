"""Rule-based progression suggestions (double progression with plateau deloads)."""

from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass
from enum import StrEnum

import pandas as pd

from gym_tracker.analysis.loader import TrainingLog
from gym_tracker.analysis.metrics import detect_plateaus, session_bests, working_sets


class Action(StrEnum):
    INCREASE_LOAD = "increase_load"
    INCREASE_REPS = "increase_reps"
    HOLD = "hold"
    DELOAD = "deload"


@dataclass(frozen=True)
class ProgressionRules:
    load_increment_kg: float = 2.5
    max_rpe_to_progress: float = 8.0
    easy_rpe: float = 7.0
    deload_factor: float = 0.9
    plateau_window: int = 3


DEFAULT_RULES = ProgressionRules()


@dataclass(frozen=True)
class Recommendation:
    exercise_id: str
    exercise_name: str
    action: Action
    last_weight_kg: float
    suggested_weight_kg: float
    last_reps: tuple[int, ...]
    target_reps: int | None


def decide_progression(
    *,
    top_weight_kg: float,
    reps: Sequence[int],
    max_rpe: float | None,
    target_sets: int | None,
    target_reps: int | None,
    stalled: bool,
    rules: ProgressionRules = DEFAULT_RULES,
) -> tuple[Action, float]:
    """Choose the next step for one exercise from its last session at the top weight.

    - Stalled: deload ``deload_factor`` of the weight, rounded down to the increment.
    - Every target set hit the target reps with RPE <= ``max_rpe_to_progress``: add load.
    - Targets hit but the effort was too high: repeat the same session.
    - Targets missed: keep the weight and work towards the target reps.
    - Without a target, add load only when the effort was easy.
    """
    increment = rules.load_increment_kg
    if stalled:
        deloaded = math.floor(top_weight_kg * rules.deload_factor / increment) * increment
        return Action.DELOAD, max(0.0, deloaded)

    if target_reps is None:
        if max_rpe is not None and max_rpe <= rules.easy_rpe:
            return Action.INCREASE_LOAD, top_weight_kg + increment
        return Action.INCREASE_REPS, top_weight_kg

    sets_done = target_sets is None or len(reps) >= target_sets
    reps_done = all(rep >= target_reps for rep in reps)
    if sets_done and reps_done:
        if max_rpe is None or max_rpe <= rules.max_rpe_to_progress:
            return Action.INCREASE_LOAD, top_weight_kg + increment
        return Action.HOLD, top_weight_kg
    return Action.INCREASE_REPS, top_weight_kg


def _optional_int(value: object) -> int | None:
    return None if pd.isna(value) else int(value)  # type: ignore[call-overload]


def recommend(log: TrainingLog, rules: ProgressionRules = DEFAULT_RULES) -> list[Recommendation]:
    """Suggest the next step for every exercise, based on its most recent session."""
    work = working_sets(log)
    if work.empty:
        return []

    plateaus = detect_plateaus(session_bests(work), window=rules.plateau_window)
    stalled_ids = set(plateaus.loc[plateaus["stalled"].astype(bool), "exercise_id"])
    names = log.exercises.set_index("exercise_id")["name"].to_dict()
    targets = log.routine_exercises.set_index(["routine_id", "exercise_id"])

    recommendations = []
    for group_key, exercise_sets in work.groupby("exercise_id", sort=True):
        exercise_id = str(group_key)
        last_session = exercise_sets[exercise_sets["workout_id"] == exercise_sets["workout_id"].iloc[-1]]
        top_weight = float(last_session["weight_kg"].max())
        top_sets = last_session[last_session["weight_kg"] == top_weight]
        reps = tuple(int(rep) for rep in top_sets["reps"])
        max_rpe = top_sets["rpe"].max()

        key = (last_session["routine_id"].iloc[0], exercise_id)
        target = targets.loc[key] if key in targets.index else None
        target_sets = _optional_int(target["target_sets"]) if target is not None else None
        target_reps = _optional_int(target["target_reps"]) if target is not None else None

        action, suggested_weight = decide_progression(
            top_weight_kg=top_weight,
            reps=reps,
            max_rpe=None if pd.isna(max_rpe) else float(max_rpe),
            target_sets=target_sets,
            target_reps=target_reps,
            stalled=exercise_id in stalled_ids,
            rules=rules,
        )
        recommendations.append(
            Recommendation(
                exercise_id=exercise_id,
                exercise_name=str(names.get(exercise_id, exercise_id)),
                action=action,
                last_weight_kg=top_weight,
                suggested_weight_kg=suggested_weight,
                last_reps=reps,
                target_reps=target_reps,
            )
        )
    return recommendations
