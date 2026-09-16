"""Training analytics: load the log, compute metrics and suggest progressions."""

from gym_tracker.analysis.loader import SCHEMAS, TrainingLog, load_training_log
from gym_tracker.analysis.metrics import (
    detect_plateaus,
    estimate_1rm,
    personal_records,
    session_bests,
    weekly_volume_by_muscle,
    weekly_weight_change,
    weight_trend,
    working_sets,
)
from gym_tracker.analysis.recommendations import (
    Action,
    PerformedSet,
    PlannedSet,
    ProgressionRules,
    Recommendation,
    decide_progression,
    recommend,
)

__all__ = [
    "SCHEMAS",
    "Action",
    "PerformedSet",
    "PlannedSet",
    "ProgressionRules",
    "Recommendation",
    "TrainingLog",
    "decide_progression",
    "detect_plateaus",
    "estimate_1rm",
    "load_training_log",
    "personal_records",
    "recommend",
    "session_bests",
    "weekly_volume_by_muscle",
    "weekly_weight_change",
    "weight_trend",
    "working_sets",
]
