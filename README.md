# Gym Tracker

Web app to log gym workouts, track body measurements and use data analysis to decide when to
change routines, exercises or intensity.

> Personal project and portfolio piece. Single user for now, designed to grow into multi-user.

## Stack

| Area | Technology |
| --- | --- |
| Frontend | React 19, TypeScript, Vite, Tailwind CSS, TanStack Query, React Router, Recharts |
| Backend | Python 3.12, FastAPI, SQLAlchemy, Alembic, Pydantic |
| Data analysis | pandas, NumPy (scikit-learn planned) |
| Database | PostgreSQL 18 (Docker) |
| Tooling | uv, Ruff, mypy, pytest · pnpm, oxlint, Prettier, Vitest |
| CI | GitHub Actions |

## Repository layout

```
backend/    Python package: analytics engine (API coming next)
frontend/   React single-page app
data/       Interim CSV training log, imported into the database later
docker-compose.yml   Local PostgreSQL
```

## Getting started

Requirements: Docker, [uv](https://docs.astral.sh/uv/), Node.js 24 and pnpm.

```bash
cp .env.example .env          # then set POSTGRES_PASSWORD
docker compose up -d --wait   # start PostgreSQL

cd backend
uv sync
uv run gym-report             # training report from data/

cd ../frontend
pnpm install
pnpm dev                      # http://localhost:5173
```

## Roadmap

- [x] Interim CSV training log and analytics engine (e1RM, PRs, weekly volume, weight trend, plateaus, progression)
- [x] App foundation: frontend shell, PostgreSQL in Docker, CI
- [ ] Backend API: models, migrations, JWT auth, CRUD for exercises, routines, workouts and measurements
- [ ] Frontend: log a workout live (mobile first), routines, measurements
- [ ] Performance dashboard with charts and recommendations
- [ ] Deployment and demo data
- [ ] Smarter recommendations, offline PWA, natural-language workout logging
