# gym-tracker (backend)

FastAPI service and analytics engine for the gym tracker.

## Features

- **API** (`/api`): health check and cookie-based JWT authentication (`login`, `logout`, `me`).
  Interactive docs at `http://localhost:8000/docs`.
- **Database**: SQLAlchemy 2.0 models for users, exercises, routines, workouts, sets and body
  measurements, with Alembic migrations and named constraints.
- **Security**: Argon2 password hashing, signed tokens in an `HttpOnly`, `SameSite=Lax` cookie.
- **Analytics** (`gym_tracker.analysis`): estimated 1RM (Epley), personal records, weekly hard
  sets per muscle group, body weight trend, plateau detection and rule-based double progression.

## Development

Requires [uv](https://docs.astral.sh/uv/) and Docker. Settings are read from `GYM_*` variables
in the repository `.env` (see `../.env.example`).

```bash
uv sync                                   # install dependencies
docker compose up -d --wait               # from the repo root: start PostgreSQL
uv run alembic upgrade head               # apply migrations
uv run gym-admin create-user --email you@example.com
uv run uvicorn gym_tracker.main:create_app --factory --reload

uv run gym-report                         # training report from ../data (Spanish output)
```

### Quality checks

```bash
uv run pytest --cov=gym_tracker   # API tests start a disposable PostgreSQL with testcontainers
uv run ruff check . && uv run ruff format --check .
uv run mypy
```

### Migrations

```bash
uv run alembic revision --autogenerate -m "describe the change"
uv run alembic upgrade head
```

A test (`test_migrations_match_models`) fails if a model change has no migration.
