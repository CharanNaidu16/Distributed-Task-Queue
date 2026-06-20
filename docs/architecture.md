# Architecture & Design Notes

## Components

```
                    ┌──────────────┐
   Browser  ─────►  │  React SPA   │  (Vite build, served by nginx on :8080)
                    └──────┬───────┘
                           │  HTTP /api/* (proxied by nginx -> api:8000)
                           ▼
                    ┌──────────────┐        enqueue job        ┌──────────────┐
                    │  FastAPI API │ ─────────────────────────►│    Redis     │
                    │  (producer)  │ ◄───────────────────────── │  queue +     │
                    └──────────────┘   read status / result    │  results     │
                                                                └──────┬───────┘
                                                          pop job /     │
                                                          write result  ▼
                                                                ┌──────────────┐
                                                                │  RQ Worker(s)│  scale to N
                                                                └──────────────┘
```

| Service | Image | Role |
|---------|-------|------|
| `redis` | `redis:7-alpine` | The queue + result/metadata store |
| `api` | `backend/Dockerfile` | FastAPI producer — accepts jobs, reports status |
| `worker` | `backend/Dockerfile` (same image) | RQ consumer — runs jobs |
| `frontend` | `frontend/Dockerfile` | nginx serving the React build, proxies `/api` |

The `api` and `worker` deliberately share one image. Build once; the role is decided purely by the
start command in `docker-compose.yml`. This mirrors how real systems ship one artifact and run it in
different modes.

## Request → result lifecycle

1. Client `POST /jobs` → FastAPI validates with Pydantic (`schemas.py`).
2. `job_service.submit_job` looks up the function in the **task registry** and `enqueue`s it onto the
   priority queue with a `Retry` policy and timeout.
3. RQ serializes the job into Redis. The API returns `202` + `job_id` immediately.
4. A worker pops the job, runs the function, and writes the result (or exception) back to Redis.
5. Client polls `GET /jobs/{id}` (the dashboard polls `GET /jobs` every 2s).

## Reliability model

- **At-least-once delivery.** A job may run more than once (e.g. worker dies mid-run, or a retry). Tasks
  are therefore written to be **idempotent** — outputs are derived from inputs (deterministic filenames).
- **Retry with backoff.** `Retry(max=3, interval=[10, 30, 60])`. Exhausted jobs go to RQ's
  `FailedJobRegistry` — our **dead-letter queue**. `POST /jobs/{id}/retry` requeues them manually.
- **Job timeout.** Long-running jobs are killed after `JOB_TIMEOUT` so a stuck job can't block a worker forever.
- **Graceful shutdown.** On `SIGTERM` RQ finishes the in-flight job before exiting (warm shutdown), so
  stopping/scaling containers doesn't lose work.

## Scaling

Throughput scales by adding worker containers (`--scale worker=N`); they share the queue with no
coordination code. The bottleneck then shifts to Redis or the work itself — a good thing to discuss in
interviews (where does the next bottleneck appear, and how would you address it?).

## Security choices

- Input validated by Pydantic; unknown task names rejected with `422` before any logic runs.
- A **task registry** maps a safe name → a known function. The API never imports or executes arbitrary
  code from client input.
- Configuration/secrets come from environment variables (`.env`), never hard-coded.

## Known limitations / roadmap

- Job history is volatile (Redis TTLs). PostgreSQL audit log is the planned durable extension.
- No auth yet — API-key/JWT on submission endpoints is a documented stretch goal.
- Polling instead of push; WebSocket updates would reduce latency and load.
