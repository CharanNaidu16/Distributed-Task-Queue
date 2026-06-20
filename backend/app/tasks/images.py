"""Image thumbnail task — a CPU-bound example of real work.

Generates a solid-colour source image (so the demo needs no uploads) and writes
a downscaled thumbnail to the shared storage volume.
"""
import os
import time

from PIL import Image

from app.config import get_settings


def generate_thumbnail(
    width: int = 800, height: int = 600, size: int = 128, color: str = "steelblue"
) -> dict:
    """Create an image and a thumbnail; return metadata about the output.

    Idempotency note: the output filename is derived from the inputs, so running
    the same job twice produces the same file (safe to retry).
    """
    settings = get_settings()
    os.makedirs(settings.storage_dir, exist_ok=True)

    # Simulate non-trivial work so concurrency/scaling is observable.
    time.sleep(1)

    source = Image.new("RGB", (width, height), color)
    thumb = source.copy()
    thumb.thumbnail((size, size))

    filename = f"thumb_{width}x{height}_{size}_{color}.png"
    out_path = os.path.join(settings.storage_dir, filename)
    thumb.save(out_path)

    return {
        "output": out_path,
        "thumbnail_size": list(thumb.size),
        "source_size": [width, height],
    }
