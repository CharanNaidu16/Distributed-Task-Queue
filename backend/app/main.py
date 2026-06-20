"""FastAPI application entrypoint.

Wires up CORS (so the React dev server can call us) and registers the routers.
Run with:  uvicorn app.main:app
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import health, jobs
from app.config import get_settings

settings = get_settings()

app = FastAPI(
    title="Distributed Task Queue",
    description="A Redis/RQ-backed job queue: submit work, run it on scalable workers, track status.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(jobs.router)


@app.get("/", tags=["root"])
def root() -> dict:
    return {"service": "distributed-task-queue", "docs": "/docs"}
