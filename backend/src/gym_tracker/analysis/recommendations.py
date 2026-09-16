"""Rule-based progression suggestions (double progression per planned set, with plateau deloads)."""

from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass
from enum import StrEnum
from typing import Any

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
class PerformedSet:
    reps: int
    weight_kg: float
    rpe: float | None = None


@dataclass(frozen=True)
class PlannedSet:
    reps: int | None = None
    weight_kg: float | None = None


@dataclass(frozen=True)
class Recommendation:
    exercise_id: str
    exercise_name: str
    action: Action
    last_sets: tuple[PerformedSet, ...]
    target_sets: tuple[PlannedSet, ...]
    suggested_sets: tuple[PlannedSet, ...]


def _next_weights(performed: Sequence[PerformedSet], planned: Sequence[PlannedSet]) -> list[float]:
    """Start from what was lifted in each set; sets that were not done fall back to the plan."""
    count = len(planned) or len(performed)
    weights = []
    for index in range(count):
        if index < len(performed):
            weights.append(performed[index].weight_kg)
        else:
            planned_weight = planned[index].weight_kg
            weights.append(planned_weight if planned_weight is not None else performed[-1].weight_kg)
    return weights


def decide_progression(
    *,
    performed: Sequence[PerformedSet],
    planned: Sequence[PlannedSet],
    stalled: bool,
    rules: ProgressionRules = DEFAULT_RULES,
) -> tuple[Action, tuple[PlannedSet, ...]]:
    """Choose the next step for one exercise from its working sets in the last session.

    Sets are compared in order with the routine's planned sets, so ramping the weight or the
    reps from set to set is supported. The suggestion keeps that shape and moves every set:

    - Stalled: deload ``deload_factor`` of each weight, rounded down to the increment.
    - Every planned set done with at least its target reps and RPE <= ``max_rpe_to_progress``:
      add ``load_increment_kg`` to every set.
    - Targets hit but the effort was too high: repeat the same weights.
    - Targets missed: keep the weights and work towards the target reps.
    - Without target reps, add load only when the effort was easy.
    """
    if not performed:
        raise ValueError("At least one performed set is needed")
    weights = _next_weights(performed, planned)
    reps = [planned[index].reps if planned else performed[index].reps for index in range(len(weights))]
    increment = rules.load_increment_kg
    rpes = [performed_set.rpe for performed_set in performed if performed_set.rpe is not None]
    max_rpe = max(rpes) if rpes else None

    def suggest(action: Action, new_weights: Sequence[float]) -> tuple[Action, tuple[PlannedSet, ...]]:
        return action, tuple(
            PlannedSet(reps=rep, weight_kg=weight) for rep, weight in zip(reps, new_weights, strict=True)
        )

    if stalled:
        return suggest(
            Action.DELOAD,
            [max(0.0, math.floor(weight * rules.deload_factor / increment) * increment) for weight in weights],
        )

    heavier = [weight + increment for weight in weights]
    if not any(planned_set.reps is not None for planned_set in planned):
        if max_rpe is not None and max_rpe <= rules.easy_rpe:
            return suggest(Action.INCREASE_LOAD, heavier)
        return suggest(Action.INCREASE_REPS, weights)

    targets_hit = len(performed) >= len(planned) and all(
        planned_set.reps is None or performed_set.reps >= planned_set.reps
        for planned_set, performed_set in zip(planned, performed, strict=False)
    )
    if not targets_hit:
        return suggest(Action.INCREASE_REPS, weights)
    if max_rpe is None or max_rpe <= rules.max_rpe_to_progress:
        return suggest(Action.INCREASE_LOAD, heavier)
    return suggest(Action.HOLD, weights)


def _optional_int(value: Any) -> int | None:
    return None if pd.isna(value) else int(value)


def _optional_float(value: Any) -> float | None:
    return None if pd.isna(value) else float(value)


def _planned_sets(log: TrainingLog) -> dict[tuple[str, str], tuple[PlannedSet, ...]]:
    """Planned sets per (routine, exercise); an exercise listed twice in a routine uses its first slot."""
    rows = log.routine_exercises.dropna(subset=["set_number"]).sort_values(["position", "set_number"])
    plans: dict[tuple[str, str], tuple[PlannedSet, ...]] = {}
    for (routine_id, exercise_id), slot_sets in rows.groupby(["routine_id", "exercise_id"], sort=False):
        first_slot = slot_sets[slot_sets["position"] == slot_sets["position"].iloc[0]]
        plans[(str(routine_id), str(exercise_id))] = tuple(
            PlannedSet(
                reps=_optional_int(row["target_reps"]),
                weight_kg=_optional_float(row["target_weight_kg"]),
            )
            for row in first_slot.to_dict(orient="records")
        )
    return plans


def recommend(log: TrainingLog, rules: ProgressionRules = DEFAULT_RULES) -> list[Recommendation]:
    """Suggest the next session for every exercise, based on its most recent one."""
    work = working_sets(log)
    if work.empty:
        return []

    plateaus = detect_plateaus(session_bests(work), window=rules.plateau_window)
    stalled_ids = set(plateaus.loc[plateaus["stalled"].astype(bool), "exercise_id"])
    names = log.exercises.set_index("exercise_id")["name"].to_dict()
    plans = _planned_sets(log)

    recommendations = []
    for group_key, exercise_sets in work.groupby("exercise_id", sort=True):
        exercise_id = str(group_key)
        last_session = exercise_sets[exercise_sets["workout_id"] == exercise_sets["workout_id"].iloc[-1]]
        performed = tuple(
            PerformedSet(
                reps=int(row["reps"]),
                weight_kg=float(row["weight_kg"]),
                rpe=_optional_float(row["rpe"]),
            )
            for row in last_session.to_dict(orient="records")
        )
        planned = plans.get((str(last_session["routine_id"].iloc[0]), exercise_id), ())
        action, suggested = decide_progression(
            performed=performed, planned=planned, stalled=exercise_id in stalled_ids, rules=rules
        )
        recommendations.append(
            Recommendation(
                exercise_id=exercise_id,
                exercise_name=str(names.get(exercise_id, exercise_id)),
                action=action,
                last_sets=performed,
                target_sets=planned,
                suggested_sets=suggested,
            )
        )
    return recommendations
