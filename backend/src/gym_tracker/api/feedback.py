"""Comments sent from the app about how it works."""

from __future__ import annotations

from fastapi import APIRouter, status

from gym_tracker.api.deps import CurrentUser, RateLimiterDep, SessionDep
from gym_tracker.models import Feedback
from gym_tracker.rate_limit import FEEDBACK_PER_USER, Check
from gym_tracker.schemas import FeedbackIn

router = APIRouter(prefix="/feedback", tags=["feedback"])


@router.post("", status_code=status.HTTP_204_NO_CONTENT)
def send_feedback(payload: FeedbackIn, session: SessionDep, user: CurrentUser, limiter: RateLimiterDep) -> None:
    """Store a comment for the developer, who reads them with ``gym-admin feedback``."""
    limiter.hit(Check(FEEDBACK_PER_USER, ("feedback", str(user.id))))
    session.add(Feedback(user_id=user.id, message=payload.message, page=payload.page))
    session.commit()
