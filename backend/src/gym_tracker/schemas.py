"""Request and response models of the HTTP API."""

from __future__ import annotations

from datetime import date, datetime
from typing import ClassVar, Self

from pydantic import AwareDatetime, BaseModel, ConfigDict, EmailStr, Field, model_validator

from gym_tracker.enums import Equipment, MuscleGroup
from gym_tracker.slugs import SLUG_PATTERN
from gym_tracker.users import MIN_PASSWORD_LENGTH


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class InputModel(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, use_enum_values=True)


class PartialUpdate(InputModel):
    """PATCH body: omitted fields stay unchanged; ``non_nullable_fields`` cannot be sent as null."""

    non_nullable_fields: ClassVar[frozenset[str]] = frozenset()

    @model_validator(mode="after")
    def reject_nulls(self) -> Self:
        nulls = sorted(
            field
            for field in self.non_nullable_fields
            if field in self.model_fields_set and getattr(self, field) is None
        )
        if nulls:
            raise ValueError(f"Fields cannot be null: {', '.join(nulls)}")
        return self


# Auth and health


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=MIN_PASSWORD_LENGTH, max_length=128)


class UserRead(ORMModel):
    id: int
    email: EmailStr
    created_at: datetime


class HealthRead(BaseModel):
    status: str
    database: str


# Exercises


class ExerciseCreate(InputModel):
    name: str = Field(min_length=1, max_length=100)
    slug: str | None = Field(default=None, max_length=100, pattern=SLUG_PATTERN)
    muscle_group: MuscleGroup
    secondary_muscles: list[MuscleGroup] = Field(default_factory=list, max_length=6)
    equipment: Equipment | None = None


class ExerciseUpdate(PartialUpdate):
    non_nullable_fields: ClassVar[frozenset[str]] = frozenset({"name", "muscle_group", "secondary_muscles"})

    name: str | None = Field(default=None, min_length=1, max_length=100)
    muscle_group: MuscleGroup | None = None
    secondary_muscles: list[MuscleGroup] | None = Field(default=None, max_length=6)
    equipment: Equipment | None = None


class ExerciseRead(ORMModel):
    id: int
    slug: str
    name: str
    muscle_group: MuscleGroup
    secondary_muscles: list[MuscleGroup]
    equipment: Equipment | None
    is_custom: bool


# Routines


class RoutineExerciseIn(InputModel):
    exercise_id: int
    target_sets: int | None = Field(default=None, ge=1, le=20)
    target_reps: int | None = Field(default=None, ge=1, le=100)
    target_weight_kg: float | None = Field(default=None, ge=0, le=1000)
    target_rpe: float | None = Field(default=None, ge=1, le=10)


class RoutineIn(InputModel):
    name: str = Field(min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=2000)
    exercises: list[RoutineExerciseIn] = Field(default_factory=list, max_length=30)


class RoutineExerciseRead(ORMModel):
    id: int
    position: int
    exercise: ExerciseRead
    target_sets: int | None
    target_reps: int | None
    target_weight_kg: float | None
    target_rpe: float | None


class RoutineRead(ORMModel):
    id: int
    name: str
    description: str | None
    created_at: datetime
    exercises: list[RoutineExerciseRead]


# Workouts


class WorkoutSetIn(InputModel):
    exercise_id: int
    set_number: int = Field(ge=1, le=50)
    reps: int = Field(ge=0, le=200)
    weight_kg: float = Field(ge=0, le=1000)
    rpe: float | None = Field(default=None, ge=1, le=10)
    is_warmup: bool = False


class WorkoutIn(InputModel):
    routine_id: int | None = None
    started_at: AwareDatetime
    ended_at: AwareDatetime | None = None
    notes: str | None = Field(default=None, max_length=2000)
    sets: list[WorkoutSetIn] = Field(default_factory=list, max_length=300)

    @model_validator(mode="after")
    def check_consistency(self) -> Self:
        if self.ended_at is not None and self.ended_at < self.started_at:
            raise ValueError("ended_at cannot be before started_at")
        keys = [(workout_set.exercise_id, workout_set.set_number) for workout_set in self.sets]
        if len(keys) != len(set(keys)):
            raise ValueError("Each exercise can use a set number only once")
        return self


class WorkoutSetRead(ORMModel):
    id: int
    exercise_id: int
    set_number: int
    reps: int
    weight_kg: float
    rpe: float | None
    is_warmup: bool


class WorkoutRead(ORMModel):
    id: int
    routine_id: int | None
    started_at: datetime
    ended_at: datetime | None
    notes: str | None
    sets: list[WorkoutSetRead]


class LastSessionRead(BaseModel):
    workout_id: int
    started_at: datetime
    sets: list[WorkoutSetRead]


# Body measurements

MEASUREMENT_FIELDS = ("weight_kg", "body_fat_pct", "waist_cm", "chest_cm", "arm_cm", "thigh_cm")


class BodyMeasurementIn(InputModel):
    measured_on: date
    weight_kg: float | None = Field(default=None, gt=0, le=500)
    body_fat_pct: float | None = Field(default=None, ge=0, le=100)
    waist_cm: float | None = Field(default=None, gt=0, le=300)
    chest_cm: float | None = Field(default=None, gt=0, le=300)
    arm_cm: float | None = Field(default=None, gt=0, le=300)
    thigh_cm: float | None = Field(default=None, gt=0, le=300)
    notes: str | None = Field(default=None, max_length=2000)

    @model_validator(mode="after")
    def require_a_measurement(self) -> Self:
        if all(getattr(self, field) is None for field in MEASUREMENT_FIELDS):
            raise ValueError(f"Provide at least one of: {', '.join(MEASUREMENT_FIELDS)}")
        return self


class BodyMeasurementRead(ORMModel):
    id: int
    measured_on: date
    weight_kg: float | None
    body_fat_pct: float | None
    waist_cm: float | None
    chest_cm: float | None
    arm_cm: float | None
    thigh_cm: float | None
    notes: str | None
