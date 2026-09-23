"""workout client id

Lets the device that logged a workout name it, so a workout queued offline and sent again after a
dropped connection is recognised instead of saved twice. Workouts saved before have none.

Revision ID: 7c1e5b9d3a40
Revises: f2aa6d776f7e
Create Date: 2026-09-23 11:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "7c1e5b9d3a40"
down_revision: str | Sequence[str] | None = "f2aa6d776f7e"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("workouts", sa.Column("client_id", sa.Uuid(), nullable=True))
    op.create_unique_constraint(op.f("uq_workouts_user_id_client_id"), "workouts", ["user_id", "client_id"])


def downgrade() -> None:
    op.drop_constraint(op.f("uq_workouts_user_id_client_id"), "workouts", type_="unique")
    op.drop_column("workouts", "client_id")
