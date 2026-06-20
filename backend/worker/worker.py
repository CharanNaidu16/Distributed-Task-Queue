"""RQ worker entrypoint.

A worker is a long-running process that listens on one or more queues, pops the
next job, runs it, and records the result/error back in Redis. Run several copies
(docker-compose up --scale worker=3) and they share the load automatically —
that is the horizontal scaling story.

RQ handles graceful shutdown for us: on SIGTERM/SIGINT it finishes the job it is
currently running before exiting (a "warm" shutdown), so work is not lost when a
container is stopped or rescheduled.
"""
import logging

from rq import Worker

from app.config import get_settings
from app.redis_conn import all_queues, get_redis

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


def main() -> None:
    settings = get_settings()
    queues = all_queues()  # drained in priority order: high -> default -> low
    logging.info("Starting worker on queues: %s", settings.queue_name_list)
    worker = Worker(queues, connection=get_redis())
    worker.work(with_scheduler=True)  # with_scheduler enables delayed/retry jobs


if __name__ == "__main__":
    main()
