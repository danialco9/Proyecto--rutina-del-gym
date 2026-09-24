"""Sending emails: through Brevo in production, to the log everywhere else."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Protocol

import httpx

from gym_tracker.config import Settings

logger = logging.getLogger(__name__)

BREVO_SEND_URL = "https://api.brevo.com/v3/smtp/email"


@dataclass(frozen=True)
class Email:
    to: str
    subject: str
    text: str
    html: str


class Mailer(Protocol):
    def send(self, email: Email) -> None: ...


class LogMailer:
    """Writes the email to the log, so a reset link can be followed locally without any account."""

    def send(self, email: Email) -> None:
        logger.warning("Email not sent (no GYM_BREVO_API_KEY) to %s: %s\n%s", email.to, email.subject, email.text)


class BrevoMailer:
    """Brevo's transactional email API (free plan: 300 emails a day)."""

    def __init__(self, api_key: str, sender_email: str, sender_name: str, client: httpx.Client | None = None) -> None:
        self._api_key = api_key
        self._sender = {"email": sender_email, "name": sender_name}
        self._client = client or httpx.Client(timeout=10)

    def send(self, email: Email) -> None:
        response = self._client.post(
            BREVO_SEND_URL,
            headers={"api-key": self._api_key, "accept": "application/json"},
            json={
                "sender": self._sender,
                "to": [{"email": email.to}],
                "subject": email.subject,
                "textContent": email.text,
                "htmlContent": email.html,
            },
        )
        response.raise_for_status()


def get_mailer(settings: Settings) -> Mailer:
    if settings.brevo_api_key is None or settings.mail_from is None:
        return LogMailer()
    return BrevoMailer(settings.brevo_api_key.get_secret_value(), settings.mail_from, settings.mail_from_name)
