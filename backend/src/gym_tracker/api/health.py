"""Liveness endpoint that also checks database connectivity."""

from __future__ import annotations

from fastapi import APIRouter
from sqlalchemy import text

from gym_tracker.api.deps import SessionDep
from gym_tracker.schemas import HealthRead

router = APIRouter(tags=["health"])


@router.get("/health")
def health(session: SessionDep) -> HealthRead:
    session.execute(text("SELECT 1"))
    return HealthRead(status="ok", database="ok")
