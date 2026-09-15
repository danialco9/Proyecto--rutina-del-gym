"""Load the interim CSV training log into typed pandas DataFrames."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import pandas as pd

ColumnKind = Literal["str", "float", "date", "bool"]

# Column order matches the CSV templates in data/ and the planned database schema.
SCHEMAS: dict[str, dict[str, ColumnKind]] = {
    "exercises": {
        "exercise_id": "str",
        "name": "str",
        "muscle_group": "str",
        "secondary_muscles": "str",
        "equipment": "str",
    },
    "routines": {
        "routine_id": "str",
        "name": "str",
        "description": "str",
    },
    "routine_exercises": {
        "routine_id": "str",
        "exercise_id": "str",
        "position": "float",
        "target_sets": "float",
        "target_reps": "float",
        "target_weight_kg": "float",
        "target_rpe": "float",
    },
    "workouts": {
        "workout_id": "str",
        "date": "date",
        "routine_id": "str",
        "notes": "str",
    },
    "workout_sets": {
        "workout_id": "str",
        "exercise_id": "str",
        "set_number": "float",
        "reps": "float",
        "weight_kg": "float",
        "rpe": "float",
        "is_warmup": "bool",
    },
    "body_measurements": {
        "date": "date",
        "weight_kg": "float",
        "body_fat_pct": "float",
        "waist_cm": "float",
        "chest_cm": "float",
        "arm_cm": "float",
        "thigh_cm": "float",
        "notes": "str",
    },
}


@dataclass(frozen=True)
class TrainingLog:
    """All tables of the training log."""

    exercises: pd.DataFrame
    routines: pd.DataFrame
    routine_exercises: pd.DataFrame
    workouts: pd.DataFrame
    workout_sets: pd.DataFrame
    body_measurements: pd.DataFrame


def _read_table(path: Path, schema: dict[str, ColumnKind]) -> pd.DataFrame:
    raw = pd.read_csv(path, dtype=str)
    missing = [column for column in schema if column not in raw.columns]
    if missing:
        raise ValueError(f"{path.name} is missing columns: {', '.join(missing)}")

    table = raw[list(schema)].copy()
    for column, kind in schema.items():
        values = table[column].str.strip()
        if kind == "date":
            table[column] = pd.to_datetime(values, format="%Y-%m-%d")
        elif kind == "float":
            table[column] = pd.to_numeric(values).astype(float)
        elif kind == "bool":
            normalized = values.str.lower()
            invalid = normalized.notna() & ~normalized.isin(["true", "false"])
            if invalid.any():
                raise ValueError(f"{path.name}: column {column} must be 'true' or 'false'")
            table[column] = normalized.eq("true").astype(bool)
        else:
            table[column] = values
    return table


def load_training_log(data_dir: Path) -> TrainingLog:
    """Read every CSV table from ``data_dir``."""
    tables = {name: _read_table(data_dir / f"{name}.csv", schema) for name, schema in SCHEMAS.items()}
    return TrainingLog(**tables)
