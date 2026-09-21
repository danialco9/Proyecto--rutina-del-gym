"""HTTP API routers."""

from fastapi import APIRouter

from gym_tracker.api import auth, dictation, exercises, health, history, measurements, progress, routines, workouts

api_router = APIRouter(prefix="/api")
for module in (health, auth, exercises, history, routines, workouts, measurements, progress, dictation):
    api_router.include_router(module.router)
