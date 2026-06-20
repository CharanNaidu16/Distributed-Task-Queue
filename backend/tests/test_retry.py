"""Retry, dead-letter, and requeue behaviour."""
from app.config import get_settings
from app.redis_conn import get_queue
from app.services import job_service
from app.tasks.emails import send_email


def test_submit_attaches_retry_budget(client):
    """Every submitted job carries the configured retry budget."""
    job = job_service.submit_job(task="report", params={}, priority="default")
    assert job.retries_left == get_settings().job_max_retries


def test_failing_job_lands_in_dead_letter(fake_redis, run_worker, monkeypatch):
    """A job that always fails ends up in the failed registry (our dead-letter)."""
    monkeypatch.setattr(get_settings(), "email_failure_rate", 1.0)  # always fail

    # Enqueue with no retry so it fails terminally in a single burst.
    queue = get_queue("default")
    job = queue.enqueue(send_email, retry=None)

    run_worker()

    data = job_service.get_job(job.id)
    assert data["status"] == "failed"
    assert "Transient failure" in data["error"]


def test_requeue_brings_failed_job_back(fake_redis, run_worker, monkeypatch):
    monkeypatch.setattr(get_settings(), "email_failure_rate", 1.0)
    queue = get_queue("default")
    job = queue.enqueue(send_email, retry=None)
    run_worker()
    assert job_service.get_job(job.id)["status"] == "failed"

    requeued = job_service.requeue_job(job.id)
    assert requeued["status"] == "queued"
