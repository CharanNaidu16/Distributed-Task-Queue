"""Health check — confirms the API is up AND can reach Redis."""
from fastapi import APIRouter

from app.redis_conn import get_redis

router = APIRouter(tags=["health"])


@router.get("/health")
def health() -> dict:
    try:
        get_redis().ping()
        redis_ok = True
    except Exception:
        redis_ok = False
    return {"status": "ok" if redis_ok else "degraded", "redis": "ok" if redis_ok else "down"}
