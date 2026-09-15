"""Database models for users, exercises, routines, workouts and body measurements."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    false,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

from gym_tracker.db import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(320), unique=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Exercise(Base):
    """An exercise from the shared catalog (``user_id`` is null) or created by a user."""

    __tablename__ = "exercises"
    __table_args__ = (UniqueConstraint("user_id", "slug", postgresql_nulls_not_distinct=True),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    slug: Mapped[str] = mapped_column(String(100))
    name: Mapped[str] = mapped_column(String(100))
    muscle_group: Mapped[str] = mapped_column(String(40))
    secondary_muscles: Mapped[list[str]] = mapped_column(ARRAY(String(40)), server_default=text("'{}'"))
    equipment: Mapped[str | None] = mapped_column(String(40))

    @property
    def is_custom(self) -> bool:
        return self.user_id is not None


class Routine(Base):
    __tablename__ = "routines"
    __table_args__ = (UniqueConstraint("user_id", "name"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(100))
    description: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    exercises: Mapped[list[RoutineExercise]] = relationship(
        back_populates="routine", cascade="all, delete-orphan", order_by="RoutineExercise.position"
    )


class RoutineExercise(Base):
    """An exercise slot in a routine, with optional targets."""

    __tablename__ = "routine_exercises"
    __table_args__ = (
        UniqueConstraint("routine_id", "position"),
        CheckConstraint("target_sets > 0", name="target_sets_positive"),
        CheckConstraint("target_reps > 0", name="target_reps_positive"),
        CheckConstraint("target_weight_kg >= 0", name="target_weight_non_negative"),
        CheckConstraint("target_rpe BETWEEN 1 AND 10", name="target_rpe_range"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    routine_id: Mapped[int] = mapped_column(ForeignKey("routines.id", ondelete="CASCADE"))
    exercise_id: Mapped[int] = mapped_column(ForeignKey("exercises.id", ondelete="RESTRICT"), index=True)
    position: Mapped[int]
    target_sets: Mapped[int | None]
    target_reps: Mapped[int | None]
    target_weight_kg: Mapped[Decimal | None] = mapped_column(Numeric(6, 2))
    target_rpe: Mapped[Decimal | None] = mapped_column(Numeric(3, 1))

    routine: Mapped[Routine] = relationship(back_populates="exercises")
    exercise: Mapped[Exercise] = relationship()


class Workout(Base):
    """A training session, optionally started from a routine."""

    __tablename__ = "workouts"
    __table_args__ = (CheckConstraint("ended_at IS NULL OR ended_at >= started_at", name="ended_after_started"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    routine_id: Mapped[int | None] = mapped_column(ForeignKey("routines.id", ondelete="SET NULL"), index=True)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    notes: Mapped[str | None] = mapped_column(Text)

    sets: Mapped[list[WorkoutSet]] = relationship(
        back_populates="workout", cascade="all, delete-orphan", order_by="WorkoutSet.id"
    )


class WorkoutSet(Base):
    """One performed set. ``set_number`` counts per exercise within the workout."""

    __tablename__ = "workout_sets"
    __table_args__ = (
        UniqueConstraint("workout_id", "exercise_id", "set_number"),
        CheckConstraint("set_number > 0", name="set_number_positive"),
        CheckConstraint("reps >= 0", name="reps_non_negative"),
        CheckConstraint("weight_kg >= 0", name="weight_non_negative"),
        CheckConstraint("rpe BETWEEN 1 AND 10", name="rpe_range"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    workout_id: Mapped[int] = mapped_column(ForeignKey("workouts.id", ondelete="CASCADE"))
    exercise_id: Mapped[int] = mapped_column(ForeignKey("exercises.id", ondelete="RESTRICT"), index=True)
    set_number: Mapped[int]
    reps: Mapped[int]
    weight_kg: Mapped[Decimal] = mapped_column(Numeric(6, 2))
    rpe: Mapped[Decimal | None] = mapped_column(Numeric(3, 1))
    is_warmup: Mapped[bool] = mapped_column(default=False, server_default=false())

    workout: Mapped[Workout] = relationship(back_populates="sets")
    exercise: Mapped[Exercise] = relationship()


class BodyMeasurement(Base):
    """Body weight and circumferences, at most one entry per day."""

    __tablename__ = "body_measurements"
    __table_args__ = (
        UniqueConstraint("user_id", "measured_on"),
        CheckConstraint("weight_kg > 0", name="weight_positive"),
        CheckConstraint("body_fat_pct BETWEEN 0 AND 100", name="body_fat_pct_range"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    measured_on: Mapped[date] = mapped_column(Date)
    weight_kg: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))
    body_fat_pct: Mapped[Decimal | None] = mapped_column(Numeric(4, 1))
    waist_cm: Mapped[Decimal | None] = mapped_column(Numeric(5, 1))
    chest_cm: Mapped[Decimal | None] = mapped_column(Numeric(5, 1))
    arm_cm: Mapped[Decimal | None] = mapped_column(Numeric(5, 1))
    thigh_cm: Mapped[Decimal | None] = mapped_column(Numeric(5, 1))
    notes: Mapped[str | None] = mapped_column(Text)
