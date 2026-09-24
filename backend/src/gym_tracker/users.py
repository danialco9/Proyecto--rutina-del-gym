"""User account operations."""

from __future__ import annotations

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from gym_tracker.models import Routine, User, Workout
from gym_tracker.security import hash_password, verify_password

MIN_PASSWORD_LENGTH = 8

# Verified against when the email is unknown, so both failure paths take similar time.
_DUMMY_PASSWORD_HASH = hash_password("dummy-password-for-timing")


class UserAlreadyExistsError(Exception):
    pass


class UserNotFoundError(Exception):
    pass


def normalize_email(email: str) -> str:
    return email.strip().lower()


def get_user_by_email(session: Session, email: str) -> User | None:
    return session.scalar(select(User).where(User.email == normalize_email(email)))


def create_user(session: Session, *, email: str, password: str) -> User:
    if len(password) < MIN_PASSWORD_LENGTH:
        raise ValueError(f"Password must be at least {MIN_PASSWORD_LENGTH} characters")
    if get_user_by_email(session, email) is not None:
        raise UserAlreadyExistsError(email)
    user = User(email=normalize_email(email), password_hash=hash_password(password))
    session.add(user)
    session.flush()
    return user


def set_password(session: Session, *, email: str, password: str) -> User:
    if len(password) < MIN_PASSWORD_LENGTH:
        raise ValueError(f"Password must be at least {MIN_PASSWORD_LENGTH} characters")
    user = get_user_by_email(session, email)
    if user is None:
        raise UserNotFoundError(email)
    user.password_hash = hash_password(password)
    session.flush()
    return user


def delete_user(session: Session, user: User) -> None:
    """Delete the account and everything in it: routines, workouts, measurements, own exercises.

    Workouts and routines go first: their sets point at exercises with RESTRICT (so a used exercise
    is never deleted by accident), which would stop the cascade from the user to their own exercises.
    """
    session.execute(delete(Workout).where(Workout.user_id == user.id))
    session.execute(delete(Routine).where(Routine.user_id == user.id))
    session.execute(delete(User).where(User.id == user.id))
    session.expunge(user)


def authenticate(session: Session, *, email: str, password: str) -> User | None:
    user = get_user_by_email(session, email)
    if user is None:
        verify_password(password, _DUMMY_PASSWORD_HASH)
        return None
    return user if verify_password(password, user.password_hash) else None
