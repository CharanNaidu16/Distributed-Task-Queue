"""Pydantic models = the API contract.

Pydantic validates incoming JSON automatically: bad input returns a 422 with a
helpful error before any of our code runs. This is part of the "secure coding"
story — the API never trusts raw client input.
"""
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class TaskName(str, Enum):
    """Only these task names may be submitted. The API never executes arbitrary
    code — it maps a known name to a known function (see tasks/registry.py)."""

    thumbnail = "thumbnail"
    report = "report"
    email = "email"


class Priority(str, Enum):
    high = "high"
    default = "default"
    low = "low"


class JobSubmitRequest(BaseModel):
    task: TaskName
    params: dict[str, Any] = Field(default_factory=dict)
    priority: Priority = Priority.default


class JobSubmitResponse(BaseModel):
    job_id: str
    task: str
    status: str
    queue: str


class JobStatusResponse(BaseModel):
    job_id: str
    task: str | None = None
    status: str
    result: Any | None = None
    error: str | None = None
    retries_left: int | None = None
    enqueued_at: str | None = None
    started_at: str | None = None
    ended_at: str | None = None


class JobListResponse(BaseModel):
    counts: dict[str, int]
    jobs: list[JobStatusResponse]
