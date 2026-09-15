from pathlib import Path

import pandas as pd
import pytest

from gym_tracker.analysis import load_training_log
from tests.conftest import WriteLog

REPO_DATA_DIR = Path(__file__).resolve().parents[2] / "data"


def test_loads_empty_templates_from_repo() -> None:
    log = load_training_log(REPO_DATA_DIR)

    assert log.workout_sets.empty
    assert list(log.workout_sets.columns) == [
        "workout_id",
        "exercise_id",
        "set_number",
        "reps",
        "weight_kg",
        "rpe",
        "is_warmup",
    ]


def test_parses_column_types(write_log: WriteLog) -> None:
    data_dir = write_log(
        workouts="2026-09-15-1,2026-09-15,,",
        workout_sets="""
            2026-09-15-1,leg-press,1,12,80,,true
            2026-09-15-1,leg-press,2,10,100,8.5,false
        """,
    )

    log = load_training_log(data_dir)

    assert log.workouts["date"].iloc[0] == pd.Timestamp("2026-09-15")
    assert log.workout_sets["weight_kg"].tolist() == [80.0, 100.0]
    assert log.workout_sets["is_warmup"].tolist() == [True, False]
    assert pd.isna(log.workout_sets["rpe"].iloc[0])


def test_rejects_invalid_boolean(write_log: WriteLog) -> None:
    data_dir = write_log(workout_sets="2026-09-15-1,leg-press,1,12,80,,yes")

    with pytest.raises(ValueError, match="is_warmup"):
        load_training_log(data_dir)


def test_rejects_missing_columns(write_log: WriteLog) -> None:
    data_dir = write_log()
    (data_dir / "workouts.csv").write_text("workout_id,date\n", encoding="utf-8")

    with pytest.raises(ValueError, match="routine_id"):
        load_training_log(data_dir)
