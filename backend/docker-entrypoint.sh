#!/bin/sh
# Bring the database up to date, then serve the API.
set -e

alembic upgrade head
gym-admin seed-catalog

# Local Docker Compose recreates the demo account on every start; production resets it on a schedule.
if [ "${GYM_SEED_DEMO:-false}" = "true" ]; then
  gym-admin seed-demo
fi

# The platform's proxy is the only way in, so trust its X-Forwarded-* headers: rate limits then see
# the visitor's address instead of the proxy's.
exec uvicorn gym_tracker.main:create_app --factory \
  --host 0.0.0.0 --port "${PORT}" \
  --proxy-headers --forwarded-allow-ips="*"
