import pytest

from gym_tracker.analysis import (
    Action,
    PerformedSet,
    PlannedSet,
    decide_progression,
    load_training_log,
    recommend,
)
from tests.conftest import WriteLog

STRAIGHT_PLAN = [PlannedSet(reps=10, weight_kg=60)] * 3


def performed(*sets: tuple[float, int], rpe: float | None = 8.0) -> list[PerformedSet]:
    return [PerformedSet(reps=reps, weight_kg=weight, rpe=rpe) for weight, reps in sets]


@pytest.mark.parametrize(
    ("done", "stalled", "expected_action", "expected_weights"),
    [
        (performed((60, 10), (60, 10), (60, 10)), False, Action.INCREASE_LOAD, [62.5, 62.5, 62.5]),
        (performed((60, 10), (60, 10), (60, 10), rpe=None), False, Action.INCREASE_LOAD, [62.5, 62.5, 62.5]),
        (performed((60, 10), (60, 10), (60, 10), rpe=9.5), False, Action.HOLD, [60, 60, 60]),
        (performed((60, 10), (60, 9), (60, 8)), False, Action.INCREASE_REPS, [60, 60, 60]),
        # A missing set counts as a missed target, and its weight comes from the plan.
        (performed((60, 10), (60, 10)), False, Action.INCREASE_REPS, [60, 60, 60]),
        (performed((60, 10), (60, 10), (60, 10)), True, Action.DELOAD, [52.5, 52.5, 52.5]),
    ],
)
def test_decide_progression_with_straight_sets(
    done: list[PerformedSet], stalled: bool, expected_action: Action, expected_weights: list[float]
) -> None:
    action, suggested = decide_progression(performed=done, planned=STRAIGHT_PLAN, stalled=stalled)

    assert action is expected_action
    assert [item.weight_kg for item in suggested] == expected_weights
    assert [item.reps for item in suggested] == [10, 10, 10]


def test_decide_progression_keeps_the_shape_of_a_pyramid() -> None:
    plan = [PlannedSet(reps=12, weight_kg=60), PlannedSet(reps=10, weight_kg=70), PlannedSet(reps=8, weight_kg=80)]

    action, suggested = decide_progression(
        performed=performed((60, 12), (72.5, 10), (82.5, 8)), planned=plan, stalled=False
    )

    assert action is Action.INCREASE_LOAD
    assert suggested == (PlannedSet(12, 62.5), PlannedSet(10, 75.0), PlannedSet(8, 85.0))

    action, _ = decide_progression(performed=performed((60, 12), (72.5, 10), (82.5, 6)), planned=plan, stalled=False)
    assert action is Action.INCREASE_REPS


@pytest.mark.parametrize(
    ("rpe", "expected"),
    [
        (6.0, (Action.INCREASE_LOAD, [42.5, 42.5])),
        (8.5, (Action.INCREASE_REPS, [40, 40])),
        (None, (Action.INCREASE_REPS, [40, 40])),
    ],
)
def test_decide_progression_without_a_plan(rpe: float | None, expected: tuple[Action, list[float]]) -> None:
    action, suggested = decide_progression(performed=performed((40, 12), (40, 12), rpe=rpe), planned=[], stalled=False)

    assert (action, [item.weight_kg for item in suggested]) == expected
    assert [item.reps for item in suggested] == [12, 12]


def test_recommend_uses_latest_session_and_routine_targets(write_log: WriteLog) -> None:
    data_dir = write_log(
        exercises="lat-pulldown,Jalón al pecho,back,biceps,machine",
        routines="pull,Pull,",
        routine_exercises="""
            pull,lat-pulldown,1,1,10,,8
            pull,lat-pulldown,1,2,10,,8
            pull,lat-pulldown,1,3,10,,8
        """,
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
    assert [item.reps for item in recommendation.last_sets] == [10, 10, 10]
    assert recommendation.target_sets == (PlannedSet(reps=10),) * 3
    assert recommendation.suggested_sets == (PlannedSet(reps=10, weight_kg=52.5),) * 3


def test_recommend_empty_log(write_log: WriteLog) -> None:
    assert recommend(load_training_log(write_log())) == []
