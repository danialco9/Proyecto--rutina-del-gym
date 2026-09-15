"""create initial schema

Revision ID: f2043aa6a8c2
Revises:
Create Date: 2026-09-15 13:06:40.894267

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "f2043aa6a8c2"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_users")),
        sa.UniqueConstraint("email", name=op.f("uq_users_email")),
    )
    op.create_table(
        "body_measurements",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("measured_on", sa.Date(), nullable=False),
        sa.Column("weight_kg", sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column("body_fat_pct", sa.Numeric(precision=4, scale=1), nullable=True),
        sa.Column("waist_cm", sa.Numeric(precision=5, scale=1), nullable=True),
        sa.Column("chest_cm", sa.Numeric(precision=5, scale=1), nullable=True),
        sa.Column("arm_cm", sa.Numeric(precision=5, scale=1), nullable=True),
        sa.Column("thigh_cm", sa.Numeric(precision=5, scale=1), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.CheckConstraint("body_fat_pct BETWEEN 0 AND 100", name=op.f("ck_body_measurements_body_fat_pct_range")),
        sa.CheckConstraint("weight_kg > 0", name=op.f("ck_body_measurements_weight_positive")),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], name=op.f("fk_body_measurements_user_id_users"), ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_body_measurements")),
        sa.UniqueConstraint("user_id", "measured_on", name=op.f("uq_body_measurements_user_id_measured_on")),
    )
    op.create_table(
        "exercises",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("slug", sa.String(length=100), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("muscle_group", sa.String(length=40), nullable=False),
        sa.Column(
            "secondary_muscles", postgresql.ARRAY(sa.String(length=40)), server_default=sa.text("'{}'"), nullable=False
        ),
        sa.Column("equipment", sa.String(length=40), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name=op.f("fk_exercises_user_id_users"), ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_exercises")),
        sa.UniqueConstraint(
            "user_id", "slug", name=op.f("uq_exercises_user_id_slug"), postgresql_nulls_not_distinct=True
        ),
    )
    op.create_index(op.f("ix_exercises_user_id"), "exercises", ["user_id"], unique=False)
    op.create_table(
        "routines",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name=op.f("fk_routines_user_id_users"), ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_routines")),
        sa.UniqueConstraint("user_id", "name", name=op.f("uq_routines_user_id_name")),
    )
    op.create_table(
        "routine_exercises",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("routine_id", sa.Integer(), nullable=False),
        sa.Column("exercise_id", sa.Integer(), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("target_sets", sa.Integer(), nullable=True),
        sa.Column("target_reps", sa.Integer(), nullable=True),
        sa.Column("target_weight_kg", sa.Numeric(precision=6, scale=2), nullable=True),
        sa.Column("target_rpe", sa.Numeric(precision=3, scale=1), nullable=True),
        sa.CheckConstraint("target_reps > 0", name=op.f("ck_routine_exercises_target_reps_positive")),
        sa.CheckConstraint("target_rpe BETWEEN 1 AND 10", name=op.f("ck_routine_exercises_target_rpe_range")),
        sa.CheckConstraint("target_sets > 0", name=op.f("ck_routine_exercises_target_sets_positive")),
        sa.CheckConstraint("target_weight_kg >= 0", name=op.f("ck_routine_exercises_target_weight_non_negative")),
        sa.ForeignKeyConstraint(
            ["exercise_id"],
            ["exercises.id"],
            name=op.f("fk_routine_exercises_exercise_id_exercises"),
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["routine_id"], ["routines.id"], name=op.f("fk_routine_exercises_routine_id_routines"), ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_routine_exercises")),
        sa.UniqueConstraint("routine_id", "position", name=op.f("uq_routine_exercises_routine_id_position")),
    )
    op.create_index(op.f("ix_routine_exercises_exercise_id"), "routine_exercises", ["exercise_id"], unique=False)
    op.create_table(
        "workouts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("routine_id", sa.Integer(), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("ended_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.CheckConstraint("ended_at IS NULL OR ended_at >= started_at", name=op.f("ck_workouts_ended_after_started")),
        sa.ForeignKeyConstraint(
            ["routine_id"], ["routines.id"], name=op.f("fk_workouts_routine_id_routines"), ondelete="SET NULL"
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name=op.f("fk_workouts_user_id_users"), ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_workouts")),
    )
    op.create_index(op.f("ix_workouts_routine_id"), "workouts", ["routine_id"], unique=False)
    op.create_index(op.f("ix_workouts_user_id"), "workouts", ["user_id"], unique=False)
    op.create_table(
        "workout_sets",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("workout_id", sa.Integer(), nullable=False),
        sa.Column("exercise_id", sa.Integer(), nullable=False),
        sa.Column("set_number", sa.Integer(), nullable=False),
        sa.Column("reps", sa.Integer(), nullable=False),
        sa.Column("weight_kg", sa.Numeric(precision=6, scale=2), nullable=False),
        sa.Column("rpe", sa.Numeric(precision=3, scale=1), nullable=True),
        sa.Column("is_warmup", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.CheckConstraint("reps >= 0", name=op.f("ck_workout_sets_reps_non_negative")),
        sa.CheckConstraint("rpe BETWEEN 1 AND 10", name=op.f("ck_workout_sets_rpe_range")),
        sa.CheckConstraint("set_number > 0", name=op.f("ck_workout_sets_set_number_positive")),
        sa.CheckConstraint("weight_kg >= 0", name=op.f("ck_workout_sets_weight_non_negative")),
        sa.ForeignKeyConstraint(
            ["exercise_id"], ["exercises.id"], name=op.f("fk_workout_sets_exercise_id_exercises"), ondelete="RESTRICT"
        ),
        sa.ForeignKeyConstraint(
            ["workout_id"], ["workouts.id"], name=op.f("fk_workout_sets_workout_id_workouts"), ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_workout_sets")),
        sa.UniqueConstraint(
            "workout_id", "exercise_id", "set_number", name=op.f("uq_workout_sets_workout_id_exercise_id_set_number")
        ),
    )
    op.create_index(op.f("ix_workout_sets_exercise_id"), "workout_sets", ["exercise_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_workout_sets_exercise_id"), table_name="workout_sets")
    op.drop_table("workout_sets")
    op.drop_index(op.f("ix_workouts_user_id"), table_name="workouts")
    op.drop_index(op.f("ix_workouts_routine_id"), table_name="workouts")
    op.drop_table("workouts")
    op.drop_index(op.f("ix_routine_exercises_exercise_id"), table_name="routine_exercises")
    op.drop_table("routine_exercises")
    op.drop_table("routines")
    op.drop_index(op.f("ix_exercises_user_id"), table_name="exercises")
    op.drop_table("exercises")
    op.drop_table("body_measurements")
    op.drop_table("users")
