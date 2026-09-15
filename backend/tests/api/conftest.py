"""Fixtures for API tests against a real PostgreSQL started with testcontainers."""

from collections.abc import Iterator
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from pydantic import SecretStr
from sqlalchemy import Engine, create_engine, select
from sqlalchemy.orm import Session
from testcontainers.community.postgres import PostgresContainer

from gym_tracker.catalog import seed_catalog
from gym_tracker.config import Settings, get_settings
from gym_tracker.db import get_session
from gym_tracker.main import create_app
from gym_tracker.models import Exercise, User
from gym_tracker.users import create_user

BACKEND_DIR = Path(__file__).resolve().parents[2]
TEST_EMAIL = "dani@example.com"
TEST_PASSWORD = "correct-horse-battery"


def alembic_config(database_url: str) -> Config:
    config = Config(str(BACKEND_DIR / "alembic.ini"))
    config.set_main_option("sqlalchemy.url", database_url.replace("%", "%%"))
    config.attributes["configure_logger"] = False
    return config


def catalog_exercise_id(session: Session, slug: str) -> int:
    exercise_id = session.scalar(select(Exercise.id).where(Exercise.slug == slug, Exercise.user_id.is_(None)))
    assert exercise_id is not None, f"Unknown catalog slug: {slug}"
    return exercise_id


@pytest.fixture(scope="session")
def database_url() -> Iterator[str]:
    with PostgresContainer("postgres:18-alpine", driver="psycopg") as postgres:
        yield postgres.get_connection_url()


@pytest.fixture(scope="session")
def engine(database_url: str) -> Iterator[Engine]:
    command.upgrade(alembic_config(database_url), "head")
    engine = create_engine(database_url)
    yield engine
    engine.dispose()


@pytest.fixture
def session(engine: Engine) -> Iterator[Session]:
    """Session whose changes are rolled back after each test, even if the code commits."""
    connection = engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection, join_transaction_mode="create_savepoint")
    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()


@pytest.fixture
def settings(database_url: str) -> Settings:
    return Settings(
        database_url=database_url,
        jwt_secret=SecretStr("test-secret-that-is-at-least-32-bytes-long"),
        cookie_secure=False,
    )


@pytest.fixture
def client(session: Session, settings: Settings) -> Iterator[TestClient]:
    app = create_app(settings)
    app.dependency_overrides[get_session] = lambda: session
    app.dependency_overrides[get_settings] = lambda: settings
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def user(session: Session) -> User:
    return create_user(session, email=TEST_EMAIL, password=TEST_PASSWORD)


@pytest.fixture
def auth_client(client: TestClient, user: User) -> TestClient:
    response = client.post("/api/auth/login", json={"email": user.email, "password": TEST_PASSWORD})
    assert response.status_code == 204
    return client


@pytest.fixture
def catalog(session: Session) -> None:
    seed_catalog(session)
