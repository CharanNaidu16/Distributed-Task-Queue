"""Job endpoints: submit, get status, list, and requeue failed jobs."""
from fastapi import APIRouter, HTTPException, Query, status

from app.schemas import (
    JobListResponse,
    JobStatusResponse,
    JobSubmitRequest,
    JobSubmitResponse,
)
from app.services import job_service

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.post("", response_model=JobSubmitResponse, status_code=status.HTTP_202_ACCEPTED)
def submit_job(payload: JobSubmitRequest) -> JobSubmitResponse:
    """Accept a job and return immediately with 202 + an id.

    The work happens later on a worker — that decoupling is the whole point of a
    task queue: the client never waits for slow processing.
    """
    try:
        job = job_service.submit_job(
            task=payload.task.value,
            params=payload.params,
            priority=payload.priority.value,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return JobSubmitResponse(
        job_id=job.id,
        task=payload.task.value,
        status=job.get_status(),
        queue=payload.priority.value,
    )


@router.get("", response_model=JobListResponse)
def list_jobs(limit: int = Query(100, ge=1, le=500)) -> JobListResponse:
    """List recent jobs with per-status counts (powers the dashboard)."""
    data = job_service.list_jobs(limit=limit)
    return JobListResponse(**data)


@router.get("/{job_id}", response_model=JobStatusResponse)
def get_job(job_id: str) -> JobStatusResponse:
    data = job_service.get_job(job_id)
    if data is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return JobStatusResponse(**data)


@router.post("/{job_id}/retry", response_model=JobStatusResponse)
def retry_job(job_id: str) -> JobStatusResponse:
    """Manually requeue a failed job from the dead-letter (failed) registry."""
    data = job_service.requeue_job(job_id)
    if data is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return JobStatusResponse(**data)
