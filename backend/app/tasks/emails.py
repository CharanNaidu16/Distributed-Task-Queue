"""Mocked email task — fails randomly on purpose to demonstrate retry logic.

Real email sending is just an external I/O call that can fail transiently
(timeout, rate limit). We simulate that with a configurable failure rate so the
retry/backoff and dead-letter behaviour is visible in the dashboard.
"""
import random
import time

from app.config import get_settings


class EmailDeliveryError(Exception):
    """Raised to simulate a transient delivery failure."""


def send_email(to: str = "user@example.com", subject: str = "Hello", body: str = "") -> dict:
    """Pretend to send an email; raise sometimes so RQ retries the job."""
    settings = get_settings()
    time.sleep(0.5)

    if random.random() < settings.email_failure_rate:
        # RQ catches this, decrements the retry count, and re-enqueues with backoff.
        raise EmailDeliveryError(f"Transient failure delivering to {to}")

    return {"delivered_to": to, "subject": subject, "bytes": len(body)}
