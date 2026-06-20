"""API contract tests against a fake Redis."""


def test_health_ok(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["redis"] == "ok"


def test_submit_returns_202_and_id(client):
    resp = client.post("/jobs", json={"task": "report", "params": {}})
    assert resp.status_code == 202
    body = resp.json()
    assert body["job_id"]
    assert body["task"] == "report"
    assert body["status"] == "queued"


def test_unknown_task_rejected_by_validation(client):
    # "doesnotexist" is not in the TaskName enum -> 422 before our code runs.
    resp = client.post("/jobs", json={"task": "doesnotexist", "params": {}})
    assert resp.status_code == 422


def test_get_missing_job_returns_404(client):
    resp = client.get("/jobs/nope-not-a-real-id")
    assert resp.status_code == 404


def test_submit_then_run_then_finished(client, run_worker):
    job_id = client.post("/jobs", json={"task": "report", "params": {}}).json()["job_id"]
    run_worker()  # process the queue in-process

    resp = client.get(f"/jobs/{job_id}")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "finished"
    assert body["result"]["rows_processed"] == 1000


def test_list_jobs_reports_counts(client, run_worker):
    client.post("/jobs", json={"task": "report", "params": {}})
    run_worker()
    data = client.get("/jobs").json()
    assert data["counts"]["finished"] >= 1
    assert len(data["jobs"]) >= 1
