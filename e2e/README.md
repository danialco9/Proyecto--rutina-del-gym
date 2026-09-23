# End-to-end tests

Playwright driving the real app: a phone-sized browser against `docker compose`, so a run goes
through nginx, the FastAPI service and PostgreSQL exactly as production does. Nothing is mocked.

```bash
GYM_RATE_LIMIT_ENABLED=false docker compose up -d --wait --build   # from the repository root
cd e2e
pnpm install
pnpm exec playwright install chromium
pnpm typecheck
pnpm test
pnpm report          # opens the HTML report of the last run
```

The stack answers on <http://localhost:8080>; point the suite elsewhere with `E2E_BASE_URL`.

## How a run is set up

`tests/fixtures.ts` registers a fresh account through the API before each test and starts the test
signed in to it. Two consequences worth knowing:

- a test never reads data another one left behind, so the flows run in parallel, can be repeated
  (`pnpm exec playwright test --repeat-each=3`) and can be run again without cleaning up,
- and they never touch the public demo account, which the README points visitors at. Only
  `demo.spec.ts` uses it, and only to sign in and look.

Registering that often trips the rate limits, which is why the stack is started with
`GYM_RATE_LIMIT_ENABLED=false`. The limits have their own tests in `backend/tests`.
