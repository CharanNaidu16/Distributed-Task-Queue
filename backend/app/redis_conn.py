"""Single source of truth for the Redis connection and RQ queues.

Everything (API, worker, services) imports its connection from here so there is
exactly one place that knows how to talk to Redis.
"""
from functools import lru_cache

import redis
from rq import Queue

from app.config import get_settings


@lru_cache
def get_redis() -> redis.Redis:
    """Return a shared Redis client built from REDIS_URL."""
    settings = get_settings()
    return redis.Redis.from_url(settings.redis_url)


def get_queue(name: str = "default") -> Queue:
    """Return an RQ Queue bound to our Redis connection.

    A Queue is just a named list inside Redis. `enqueue` pushes a job onto it;
    a worker listening on that name pops and runs it.
    """
    return Queue(name, connection=get_redis())


def all_queues() -> list[Queue]:
    """All configured priority queues, highest priority first."""
    return [get_queue(n) for n in get_settings().queue_name_list]
