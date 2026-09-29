# /// script
# requires-python = ">=3.12"
# dependencies = ["pillow>=11"]
# ///
"""Download the exercise drawings the catalog uses and write their list thumbnails.

Run from `frontend/` with `uv run scripts/build_exercise_art.py`. The output is committed, so this
only needs to run again when `src/features/workout/exercise-art.json` changes.

Drawings come from workout-guide (https://github.com/bryllim/workout-guide), pinned to one commit,
and are licensed CC BY-SA 4.0 — see docs/credits.md.
"""

from __future__ import annotations

import io
import json
import urllib.request
from pathlib import Path

from PIL import Image

SOURCE_COMMIT = "aac599224bb9780305239607ef98540b7e0ce389"
SOURCE_URL = f"https://raw.githubusercontent.com/bryllim/workout-guide/{SOURCE_COMMIT}/packages/workout-guide/assets"
# The middle frame shows the movement at its most recognisable point.
THUMBNAIL_FRAME = 2
# Twice the rendered size, so it stays sharp on high-density phone screens.
THUMBNAIL_SIZE = 96
# Empty space kept around the figure once the transparent margin is trimmed.
PADDING = 0.12

FRONTEND = Path(__file__).resolve().parent.parent
ART_MAP = FRONTEND / "src" / "features" / "workout" / "exercise-art.json"
OUTPUT = FRONTEND / "public" / "exercise-art"


def thumbnail(drawing: Image.Image) -> Image.Image:
    """Trim the transparent margin and centre the figure on a square transparent canvas."""
    bbox = drawing.getbbox()
    figure = drawing.crop(bbox) if bbox else drawing
    inner = round(THUMBNAIL_SIZE * (1 - 2 * PADDING))
    figure.thumbnail((inner, inner), Image.Resampling.LANCZOS)
    canvas = Image.new("RGBA", (THUMBNAIL_SIZE, THUMBNAIL_SIZE))
    canvas.alpha_composite(
        figure, ((THUMBNAIL_SIZE - figure.width) // 2, (THUMBNAIL_SIZE - figure.height) // 2)
    )
    return canvas


def main() -> None:
    drawings = sorted(set(json.loads(ART_MAP.read_text(encoding="utf-8")).values()))
    OUTPUT.mkdir(parents=True, exist_ok=True)
    for drawing_id in drawings:
        url = f"{SOURCE_URL}/{drawing_id}/frame-{THUMBNAIL_FRAME}.png"
        with urllib.request.urlopen(url) as response:
            drawing = Image.open(io.BytesIO(response.read())).convert("RGBA")
        thumbnail(drawing).save(OUTPUT / f"{drawing_id}.webp", "WEBP", quality=80, method=6)
    stale = {path.stem for path in OUTPUT.glob("*.webp")} - set(drawings)
    for drawing_id in stale:
        (OUTPUT / f"{drawing_id}.webp").unlink()
    print(f"{len(drawings)} thumbnails in {OUTPUT.relative_to(FRONTEND)}, {len(stale)} stale removed")


if __name__ == "__main__":
    main()
