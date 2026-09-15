import pandas as pd
import pytest

from gym_tracker.analysis import (
    detect_plateaus,
    estimate_1rm,
    load_training_log,
    personal_records,
    session_bests,
    weekly_volume_by_muscle,
    weekly_weight_change,
    weight_trend,
    working_sets,
)
from tests.conftest import WriteLog

EXERCISES = """
    bench-press,Press banca,chest,triceps|shoulders,barbell
    leg-press,Prensa,quads,glutes,machine
"""
WORKOUTS = """
    w1,2026-09-14,,
    w2,2026-09-16,,
    w3,2026-09-22,,
"""
WORKOUT_SETS = """
    w1,bench-press,1,10,40,,true
    w1,bench-press,2,8,60,8,false
    w1,bench-press,3,8,60,9,false
    w2,leg-press,1,12,100,7,false
    w3,bench-press,1,5,70,9,false
"""


def test_estimate_1rm_uses_epley_and_keeps_singles() -> None:
    result = estimate_1rm(pd.Series([100.0, 100.0]), pd.Series([1.0, 10.0]))

    assert result.tolist() == pytest.approx([100.0, 133.333], abs=1e-3)


def test_working_sets_exclude_warmups(write_log: WriteLog) -> None:
    log = load_training_log(write_log(exercises=EXERCISES, workouts=WORKOUTS, workout_sets=WORKOUT_SETS))

    work = working_sets(log)

    assert len(work) == 4
    assert not work["is_warmup"].any()
    assert work["volume_kg"].iloc[0] == 480.0


def test_session_bests_and_personal_records(write_log: WriteLog) -> None:
    log = load_training_log(write_log(exercises=EXERCISES, workouts=WORKOUTS, workout_sets=WORKOUT_SETS))
    work = working_sets(log)

    bests = session_bests(work)
    records = personal_records(work).set_index("exercise_id")

    bench = bests[bests["exercise_id"] == "bench-press"]
    assert bench["working_sets"].tolist() == [2, 1]
    assert records.loc["bench-press", "max_weight_kg"] == 70.0
    assert records.loc["bench-press", "best_e1rm_kg"] == pytest.approx(81.667, abs=1e-3)
    assert records.loc["bench-press", "best_e1rm_date"] == pd.Timestamp("2026-09-22")


def test_personal_records_empty_log(write_log: WriteLog) -> None:
    assert personal_records(working_sets(load_training_log(write_log()))).empty


def test_weekly_volume_counts_hard_sets_per_muscle(write_log: WriteLog) -> None:
    log = load_training_log(write_log(exercises=EXERCISES, workouts=WORKOUTS, workout_sets=WORKOUT_SETS))

    volume = weekly_volume_by_muscle(working_sets(log), log.exercises)

    first_week = volume[volume["week_start"] == pd.Timestamp("2026-09-14")].set_index("muscle_group")
    assert first_week.loc["chest", "hard_sets"] == 2
    assert first_week.loc["quads", "volume_kg"] == 1200.0
    assert volume["week_start"].nunique() == 2


def test_weight_trend_and_weekly_change(write_log: WriteLog) -> None:
    log = load_training_log(
        write_log(
            body_measurements="""
                2026-09-01,80.0,,,,,,
                2026-09-04,,18,,,,,
                2026-09-08,79.3,,,,,,
                2026-09-15,78.6,,,,,,
            """
        )
    )

    trend = weight_trend(log.body_measurements)

    assert trend["weight_kg"].tolist() == [80.0, 79.3, 78.6]
    assert weekly_weight_change(log.body_measurements) == pytest.approx(-0.7)


def test_weekly_change_needs_two_dates(write_log: WriteLog) -> None:
    log = load_training_log(write_log(body_measurements="2026-09-01,80.0,,,,,,"))

    assert weekly_weight_change(log.body_measurements) is None


@pytest.mark.parametrize(
    ("history", "stalled"),
    [
        ([100.0, 100.5, 100.2, 100.8], True),
        ([100.0, 102.0, 104.0, 106.0], False),
    ],
)
def test_detect_plateaus(history: list[float], stalled: bool) -> None:
    bests = pd.DataFrame(
        {
            "exercise_id": "bench-press",
            "date": pd.date_range("2026-09-01", periods=len(history), freq="W"),
            "best_e1rm_kg": history,
        }
    )

    result = detect_plateaus(bests, window=3)

    assert result["stalled"].tolist() == [stalled]


def test_detect_plateaus_needs_enough_sessions() -> None:
    bests = pd.DataFrame(
        {"exercise_id": "squat", "date": pd.date_range("2026-09-01", periods=3), "best_e1rm_kg": [100.0] * 3}
    )

    assert detect_plateaus(bests, window=3).empty
