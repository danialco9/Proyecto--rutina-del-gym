"""Password reset by email: single-use links that expire.

The emailed token is random (256 bits) and only its SHA-256 is stored, so a leaked database does not
hand out working links. Using a link deletes every pending link of that account.
"""

from __future__ import annotations

import hashlib
import secrets
from datetime import datetime, timedelta
from html import escape

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from gym_tracker.mail import Email
from gym_tracker.models import PasswordResetToken, User
from gym_tracker.security import hash_password
from gym_tracker.users import MIN_PASSWORD_LENGTH


def _hash(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def create_reset_token(session: Session, user: User, *, now: datetime, ttl: timedelta) -> str:
    token = secrets.token_urlsafe(32)
    session.add(PasswordResetToken(user_id=user.id, token_hash=_hash(token), expires_at=now + ttl))
    session.flush()
    return token


def reset_password(session: Session, token: str, new_password: str, *, now: datetime) -> User | None:
    """Sets the new password if the link is valid; returns ``None`` for an unknown or expired one."""
    if len(new_password) < MIN_PASSWORD_LENGTH:
        raise ValueError(f"Password must be at least {MIN_PASSWORD_LENGTH} characters")
    stored = session.scalar(select(PasswordResetToken).where(PasswordResetToken.token_hash == _hash(token)))
    if stored is None or stored.expires_at <= now:
        return None
    user = session.get(User, stored.user_id)
    if user is None:
        return None
    user.password_hash = hash_password(new_password)
    session.execute(delete(PasswordResetToken).where(PasswordResetToken.user_id == user.id))
    session.flush()
    return user


def reset_email(to: str, link: str, ttl_minutes: int) -> Email:
    text = (
        "Hola:\n\n"
        "Has pedido cambiar la contraseña de Gym Tracker. Abre este enlace para elegir una nueva "
        f"(caduca en {ttl_minutes} minutos):\n\n{link}\n\n"
        "Si no lo has pedido tú, ignora este email: tu contraseña no cambia."
    )
    html = (
        "<p>Hola:</p>"
        "<p>Has pedido cambiar la contraseña de Gym Tracker. Pulsa el botón para elegir una nueva "
        f"(caduca en {ttl_minutes} minutos):</p>"
        f'<p><a href="{escape(link)}" style="display:inline-block;padding:12px 20px;background:#8ee14f;'
        'color:#0b0d10;border-radius:8px;text-decoration:none;font-weight:600">Elegir nueva contraseña</a></p>'
        f'<p style="color:#666;font-size:13px">Si el botón no funciona, copia este enlace: {escape(link)}</p>'
        "<p>Si no lo has pedido tú, ignora este email: tu contraseña no cambia.</p>"
    )
    return Email(to=to, subject="Recupera tu contraseña de Gym Tracker", text=text, html=html)
