# End-to-end tests

Playwright driving the real app: a phone-sized browser against `docker compose`, so a run goes
through nginx, the FastAPI service and PostgreSQL exactly as production does. Nothing is mocked.

```bash
GYM_RATE_LIMIT_ENABLED=false docker compose up -d --wait --build   # from the repository root
cd e2e
pnpm install
pnpm exec playwright install chromium
pnpm test
pnpm report          # opens the HTML report of the last run
```

The stack answers on <http://localhost:8080>; point the suite elsewhere with `E2E_BASE_URL`.

## How a run is set up

`tests/account.setup.ts` registers an account of its own through the API before anything else and
saves its session to `.auth/user.json`, which the flows then start from. Two consequences worth
knowing:

- the flows never read data another run left behind, so they can be run again without cleaning up,
- and they never touch the public demo account, which the README points visitors at. Only
  `demo.spec.ts` uses it, and only to sign in and look.

Registering and signing in that often trips the login rate limits, which is why the stack is started
with `GYM_RATE_LIMIT_ENABLED=false`. The limits have their own tests in `backend/tests`.
