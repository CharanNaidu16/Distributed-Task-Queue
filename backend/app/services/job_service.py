"""All the queue logic lives here, kept separate from the HTTP layer.

The API routers stay thin and just translate between HTTP and these functions.
"""
from typing import Any

from rq import Retry
from rq.exceptions import NoSuchJobError
from rq.job import Job
from rq.registry import (
    DeferredJobRegistry,
    FailedJobRegistry,
    FinishedJobRegistry,
    ScheduledJobRegistry,
    StartedJobRegistry,
)

from app.config import get_settings
from app.redis_conn import all_queues, get_queue, get_redis
from app.tasks.registry import get_task


def _iso(dt) -> str | None:
    return dt.isoformat() if dt else None


def submit_job(task: str, params: dict[str, Any], priority: str = "default") -> Job:
    """Enqueue a task by name onto the queue matching its priority.

    We pass the task's params via `kwargs=` (not **params) so user-supplied keys
    can never collide with RQ's own options like `retry` or `job_timeout`.
    """
    settings = get_settings()
    func = get_task(task)  # raises ValueError for unknown tasks -> 400 at the API layer
    queue = get_queue(priority)

    job = queue.enqueue(
        func,
        kwargs=params,
        retry=Retry(max=settings.job_max_retries, interval=[10, 30, 60]),
        job_timeout=settings.job_timeout,
        meta={"task": task},  # remember the friendly name for status responses
        result_ttl=3600,      # keep finished results in Redis for an hour
        failure_ttl=3600,     # keep failed jobs (the dead-letter view) for an hour
    )
    return job


def job_to_dict(job: Job) -> dict[str, Any]:
    """Flatten an RQ Job into the JSON shape the API/dashboard expect."""
    status = job.get_status(refresh=True)

    error = None
    if job.exc_info:
        # exc_info is a full traceback; show just the final, human-readable line.
        error = job.exc_info.strip().splitlines()[-1]

    return {
        "job_id": job.id,
        "task": (job.meta or {}).get("task"),
        "status": status,
        "result": job.return_value(),
        "error": error,
        "retries_left": job.retries_left,
        "enqueued_at": _iso(job.enqueued_at),
        "started_at": _iso(job.started_at),
        "ended_at": _iso(job.ended_at),
    }


def get_job(job_id: str) -> dict[str, Any] | None:
    """Fetch one job's status, or None if it no longer exists."""
    try:
        job = Job.fetch(job_id, connection=get_redis())
    except NoSuchJobError:
        return None
    return job_to_dict(job)


def _registries_for(queue):
    return {
        "queued": queue.job_ids,
        "started": StartedJobRegistry(queue=queue).get_job_ids(),
        "deferred": DeferredJobRegistry(queue=queue).get_job_ids(),
        "scheduled": ScheduledJobRegistry(queue=queue).get_job_ids(),
        "finished": FinishedJobRegistry(queue=queue).get_job_ids(),
        "failed": FailedJobRegistry(queue=queue).get_job_ids(),
    }


def list_jobs(limit: int = 100) -> dict[str, Any]:
    """Aggregate jobs across all priority queues and registries for the dashboard.

    Returns per-status counts plus the most recent jobs (newest first).
    """
    counts: dict[str, int] = {}
    job_ids: list[str] = []

    for queue in all_queues():
        for status, ids in _registries_for(queue).items():
            counts[status] = counts.get(status, 0) + len(ids)
            job_ids.extend(ids)

    # De-duplicate while preserving order, then hydrate the jobs.
    seen: set[str] = set()
    unique_ids = [jid for jid in job_ids if not (jid in seen or seen.add(jid))]

    jobs = [job_to_dict(j) for j in Job.fetch_many(unique_ids, connection=get_redis()) if j]
    # Newest first by enqueue time.
    jobs.sort(key=lambda d: d["enqueued_at"] or "", reverse=True)

    return {"counts": counts, "jobs": jobs[:limit]}


def requeue_job(job_id: str) -> dict[str, Any] | None:
    """Move a failed job back onto its queue (manual dead-letter requeue)."""
    redis = get_redis()
    try:
        job = Job.fetch(job_id, connection=redis)
    except NoSuchJobError:
        return None

    registry = FailedJobRegistry(queue=get_queue(job.origin))
    registry.requeue(job_id)
    return get_job(job_id)
