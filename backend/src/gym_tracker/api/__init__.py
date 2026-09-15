"""HTTP API routers."""

from fastapi import APIRouter

from gym_tracker.api import auth, health

api_router = APIRouter(prefix="/api")
api_router.include_router(health.router)
api_router.include_router(auth.router)
