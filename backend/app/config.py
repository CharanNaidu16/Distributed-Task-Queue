"""Central configuration, loaded from environment variables.

pydantic-settings reads each field from the matching env var (case-insensitive),
falling back to the defaults below. This keeps secrets/config out of the code.
"""
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Redis connection string. Inside docker-compose the host is the service name "redis".
    redis_url: str = "redis://localhost:6379/0"

    # CORS origins allowed to call the API (comma-separated in the env var).
    cors_origins: str = "http://localhost:5173,http://localhost:8080"

    # Queue names, highest priority first. Workers drain them in this order.
    queue_names: str = "high,default,low"

    # Reliability knobs.
    job_timeout: int = 180
    job_max_retries: int = 3

    # Where task outputs are written inside the container.
    storage_dir: str = "/app/storage"

    # Demo: how often the mocked email task fails, so retries are visible.
    email_failure_rate: float = 0.5

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def queue_name_list(self) -> list[str]:
        return [q.strip() for q in self.queue_names.split(",") if q.strip()]


@lru_cache
def get_settings() -> Settings:
    """Cached singleton so we don't re-parse the environment on every import."""
    return Settings()
