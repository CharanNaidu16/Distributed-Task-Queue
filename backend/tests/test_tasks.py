"""Unit tests for the task functions in isolation (no queue involved)."""
import os

import pytest

from app.config import get_settings
from app.tasks.images import generate_thumbnail
from app.tasks.registry import get_task
from app.tasks.reports import aggregate_csv


@pytest.fixture(autouse=True)
def tmp_storage(tmp_path, monkeypatch):
    """Write task outputs to a temp dir instead of /app/storage."""
    monkeypatch.setattr(get_settings(), "storage_dir", str(tmp_path))


def test_generate_thumbnail_writes_file():
    result = generate_thumbnail(width=400, height=300, size=64)
    assert os.path.exists(result["output"])
    assert max(result["thumbnail_size"]) <= 64


def test_aggregate_csv_sums_by_group():
    rows = [
        {"category": "a", "amount": 10},
        {"category": "a", "amount": 5},
        {"category": "b", "amount": 2},
    ]
    result = aggregate_csv(rows=rows)
    assert result["groups"] == {"a": 15.0, "b": 2.0}
    assert result["rows_processed"] == 3
    assert os.path.exists(result["output"])


def test_registry_lookup():
    assert get_task("report") is aggregate_csv
    with pytest.raises(ValueError):
        get_task("nope")
