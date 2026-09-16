"""HTTP API routers."""

from fastapi import APIRouter

from gym_tracker.api import auth, exercises, health, measurements, routines, workouts

api_router = APIRouter(prefix="/api")
for module in (health, auth, exercises, routines, workouts, measurements):
    api_router.include_router(module.router)
