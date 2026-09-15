"""Helpers shared by the resource routers."""

from __future__ import annotations

from collections.abc import Iterable

from fastapi import HTTPException, status
from sqlalchemy import ColumnElement, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from gym_tracker.models import Exercise, User

UNPROCESSABLE = 422


def not_found(resource: str) -> HTTPException:
    return HTTPException(status.HTTP_404_NOT_FOUND, detail=f"{resource} not found")


def commit_or_conflict(session: Session, detail: str) -> None:
    """Commit, turning unique or foreign key violations into ``409 Conflict``."""
    try:
        session.commit()
    except IntegrityError as error:
        session.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, detail=detail) from error


def visible_to(user: User) -> ColumnElement[bool]:
    """Catalog exercises plus the user's own custom exercises."""
    return or_(Exercise.user_id.is_(None), Exercise.user_id == user.id)


def ensure_exercises_visible(session: Session, user: User, exercise_ids: Iterable[int]) -> None:
    requested = set(exercise_ids)
    if not requested:
        return
    found = set(session.scalars(select(Exercise.id).where(Exercise.id.in_(requested), visible_to(user))))
    if missing := sorted(requested - found):
        raise HTTPException(UNPROCESSABLE, detail=f"Unknown exercise ids: {missing}")


def escape_like(value: str) -> str:
    return value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
