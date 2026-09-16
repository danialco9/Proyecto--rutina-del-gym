"""Data conversion of the migration that moved routine targets to one row per planned set."""

from collections.abc import Iterator

import pytest
from alembic import command
from sqlalchemy import Engine, create_engine, make_url, text

from tests.api.conftest import alembic_config

BEFORE = "f2043aa6a8c2"
AFTER = "f2aa6d776f7e"
DATABASE = "migration_routine_sets"


@pytest.fixture
def scratch_url(engine: Engine, database_url: str) -> Iterator[str]:
    """A separate empty database in the test server, so migrating down does not affect other tests."""
    admin = engine.execution_options(isolation_level="AUTOCOMMIT")
    with admin.connect() as connection:
        connection.execute(text(f"DROP DATABASE IF EXISTS {DATABASE}"))
        connection.execute(text(f"CREATE DATABASE {DATABASE}"))
    url = make_url(database_url).set(database=DATABASE).render_as_string(hide_password=False)
    yield url
    with admin.connect() as connection:
        connection.execute(text(f"DROP DATABASE IF EXISTS {DATABASE} WITH (FORCE)"))


def test_targets_are_expanded_into_sets_and_back(scratch_url: str) -> None:
    config = alembic_config(scratch_url)
    command.upgrade(config, BEFORE)
    scratch = create_engine(scratch_url)
    with scratch.begin() as connection:
        connection.execute(
            text(
                """
                INSERT INTO users (id, email, password_hash) VALUES (1, 'dani@example.com', 'x');
                INSERT INTO exercises (id, slug, name, muscle_group) VALUES (1, 'squat', 'Sentadilla', 'quads');
                INSERT INTO routines (id, user_id, name) VALUES (1, 1, 'Pierna');
                INSERT INTO routine_exercises
                    (id, routine_id, exercise_id, position, target_sets, target_reps, target_weight_kg, target_rpe)
                VALUES
                    (1, 1, 1, 1, 3, 8, 60, NULL),
                    (2, 1, 1, 2, NULL, 12, NULL, 8),
                    (3, 1, 1, 3, NULL, NULL, NULL, NULL);
                """
            )
        )

    command.upgrade(config, AFTER)
    with scratch.connect() as connection:
        sets = connection.execute(
            text(
                "SELECT routine_exercise_id, set_number, target_reps, target_weight_kg, target_rpe "
                "FROM routine_sets ORDER BY routine_exercise_id, set_number"
            )
        ).all()
    assert [(row[0], row[1], row[2], row[3], row[4]) for row in sets] == [
        (1, 1, 8, 60, None),
        (1, 2, 8, 60, None),
        (1, 3, 8, 60, None),
        (2, 1, 12, None, 8),
    ]

    command.downgrade(config, BEFORE)
    with scratch.connect() as connection:
        slots = connection.execute(
            text("SELECT id, target_sets, target_reps, target_weight_kg, target_rpe FROM routine_exercises ORDER BY id")
        ).all()
    scratch.dispose()
    assert [tuple(row) for row in slots] == [(1, 3, 8, 60, None), (2, 1, 12, None, 8), (3, None, None, None, None)]
