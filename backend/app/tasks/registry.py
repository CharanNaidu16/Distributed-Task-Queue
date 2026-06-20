"""Maps a safe task name -> the function that runs it.

Why a registry? The API accepts a *name* (validated against TaskName), never a
code path or import string. This prevents a client from tricking the system into
running arbitrary functions — a key secure-coding decision.
"""
from collections.abc import Callable

from app.tasks.emails import send_email
from app.tasks.images import generate_thumbnail
from app.tasks.reports import aggregate_csv

TASK_REGISTRY: dict[str, Callable] = {
    "thumbnail": generate_thumbnail,
    "report": aggregate_csv,
    "email": send_email,
}


def get_task(name: str) -> Callable:
    """Look up a task function by name, or raise if unknown."""
    try:
        return TASK_REGISTRY[name]
    except KeyError:
        raise ValueError(f"Unknown task: {name!r}") from None
