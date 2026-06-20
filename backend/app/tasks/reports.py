"""CSV aggregation task — the "data pipeline" example: ingest -> transform -> output.

Takes a list of row dicts (or generates sample rows), aggregates a numeric column
grouped by a key column, and writes the result as CSV to the storage volume.
"""
import csv
import os
import random
import time
from collections import defaultdict

from app.config import get_settings


def aggregate_csv(rows: list[dict] | None = None, group_by: str = "category", value: str = "amount") -> dict:
    """Group rows by `group_by` and sum `value`. Returns totals + output path."""
    settings = get_settings()
    os.makedirs(settings.storage_dir, exist_ok=True)

    # If no data was provided, synthesize a sample dataset so the demo is self-contained.
    if rows is None:
        categories = ["books", "electronics", "groceries", "toys"]
        rows = [
            {"category": random.choice(categories), "amount": round(random.uniform(5, 500), 2)}
            for _ in range(1000)
        ]

    time.sleep(1)  # simulate I/O / processing time

    totals: dict[str, float] = defaultdict(float)
    for row in rows:
        key = str(row.get(group_by, "unknown"))
        totals[key] += float(row.get(value, 0) or 0)

    filename = f"report_{group_by}_by_{value}.csv"
    out_path = os.path.join(settings.storage_dir, filename)
    with open(out_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([group_by, f"total_{value}"])
        for key, total in sorted(totals.items()):
            writer.writerow([key, round(total, 2)])

    return {
        "output": out_path,
        "rows_processed": len(rows),
        "groups": {k: round(v, 2) for k, v in sorted(totals.items())},
    }
