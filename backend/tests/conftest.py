"""Shared test fixtures.

We swap the real Redis for `fakeredis` (an in-memory fake) so tests need no
running Redis server, and we run jobs with RQ's SimpleWorker, which executes them
in-process (no forking) — fast and works on every OS/CI runner.
"""
import fakeredis
import pytest
import redis
from fastapi.testclient import TestClient
from rq import SimpleWorker

import app.redis_conn as redis_conn
from app.config import get_settings
from app.main import app


@pytest.fixture(autouse=True)
def tmp_storage(tmp_path, monkeypatch):
    """Point task file output at a per-test temp dir.

    The default storage dir is /app/storage (correct inside the Docker
    container), but that path isn't writable on a bare CI runner. Redirecting
    it here keeps tasks from crashing when the worker runs them in tests.
    """
    monkeypatch.setattr(get_settings(), "storage_dir", str(tmp_path))


@pytest.fixture
def fake_redis(monkeypatch):
    """One shared fake Redis instance for the whole test.

    We patch what get_redis() *returns* (redis.Redis.from_url) rather than
    get_redis itself, so every module that did `from app.redis_conn import
    get_redis` transparently gets the same fake — no per-import-site patching.
    """
    fake = fakeredis.FakeStrictRedis()
    redis_conn.get_redis.cache_clear()
    monkeypatch.setattr(redis.Redis, "from_url", classmethod(lambda cls, *a, **k: fake))
    return fake


@pytest.fixture
def client(fake_redis):
    return TestClient(app)


@pytest.fixture
def run_worker(fake_redis):
    """Drain all queues once, in-process. Returns a callable."""

    def _run():
        worker = SimpleWorker(redis_conn.all_queues(), connection=fake_redis)
        worker.work(burst=True)

    return _run


@pytest.fixture
def settings():
    return get_settings()
