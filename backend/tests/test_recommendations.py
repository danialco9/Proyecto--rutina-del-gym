import pytest

from gym_tracker.analysis import Action, decide_progression, load_training_log, recommend
from tests.conftest import WriteLog


@pytest.mark.parametrize(
    ("reps", "max_rpe", "stalled", "expected"),
    [
        ([10, 10, 10], 8.0, False, (Action.INCREASE_LOAD, 62.5)),
        ([10, 10, 10], None, False, (Action.INCREASE_LOAD, 62.5)),
        ([10, 10, 10], 9.5, False, (Action.HOLD, 60.0)),
        ([10, 9, 8], 8.0, False, (Action.INCREASE_REPS, 60.0)),
        ([10, 10], 7.0, False, (Action.INCREASE_REPS, 60.0)),
        ([10, 10, 10], 8.0, True, (Action.DELOAD, 52.5)),
    ],
)
def test_decide_progression_with_targets(
    reps: list[int], max_rpe: float | None, stalled: bool, expected: tuple[Action, float]
) -> None:
    result = decide_progression(
        top_weight_kg=60.0, reps=reps, max_rpe=max_rpe, target_sets=3, target_reps=10, stalled=stalled
    )

    assert result == expected


@pytest.mark.parametrize(
    ("max_rpe", "expected"),
    [(6.0, (Action.INCREASE_LOAD, 42.5)), (8.5, (Action.INCREASE_REPS, 40.0)), (None, (Action.INCREASE_REPS, 40.0))],
)
def test_decide_progression_without_targets(max_rpe: float | None, expected: tuple[Action, float]) -> None:
    result = decide_progression(
        top_weight_kg=40.0, reps=[12, 12], max_rpe=max_rpe, target_sets=None, target_reps=None, stalled=False
    )

    assert result == expected


def test_recommend_uses_latest_session_and_routine_targets(write_log: WriteLog) -> None:
    data_dir = write_log(
        exercises="lat-pulldown,Jalón al pecho,back,biceps,machine",
        routines="pull,Pull,",
        routine_exercises="pull,lat-pulldown,1,3,10,,8",
        workouts="""
            w1,2026-09-08,pull,
            w2,2026-09-15,pull,
        """,
        workout_sets="""
            w1,lat-pulldown,1,8,50,9,false
            w2,lat-pulldown,1,12,30,,true
            w2,lat-pulldown,2,10,50,7,false
            w2,lat-pulldown,3,10,50,8,false
            w2,lat-pulldown,4,10,50,8,false
        """,
    )

    [recommendation] = recommend(load_training_log(data_dir))

    assert recommendation.exercise_name == "Jalón al pecho"
    assert recommendation.action is Action.INCREASE_LOAD
    assert recommendation.last_reps == (10, 10, 10)
    assert recommendation.suggested_weight_kg == 52.5


def test_recommend_empty_log(write_log: WriteLog) -> None:
    assert recommend(load_training_log(write_log())) == []
