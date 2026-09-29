# /// script
# requires-python = ">=3.12"
# dependencies = ["pillow>=11"]
# ///
"""Download the exercise drawings the catalog uses and write their thumbnails and movement frames.

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
FRAMES = (1, 2, 3)
# The middle frame shows the movement at its most recognisable point.
THUMBNAIL_FRAME = 2
# Twice the rendered size, so it stays sharp on high-density phone screens.
THUMBNAIL_SIZE = 96
# The info sheet shows the frames at up to 256 px, minus padding.
FRAME_SIZE = 320
# Empty space kept around the figure once the transparent margin is trimmed.
PADDING = 0.12

FRONTEND = Path(__file__).resolve().parent.parent
ART_MAP = FRONTEND / "src" / "features" / "workout" / "exercise-art.json"
OUTPUT = FRONTEND / "public" / "exercise-art"
FRAMES_OUTPUT = OUTPUT / "frames"


def download(drawing_id: str, frame: int) -> Image.Image:
    with urllib.request.urlopen(f"{SOURCE_URL}/{drawing_id}/frame-{frame}.png") as response:
        return Image.open(io.BytesIO(response.read())).convert("RGBA")


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


def movement_frames(drawings: list[Image.Image]) -> list[Image.Image]:
    """Crop every frame to the box that holds all of them, so the figure does not jump when animated."""
    boxes = [box for drawing in drawings if (box := drawing.getbbox())]
    box = (
        (min(b[0] for b in boxes), min(b[1] for b in boxes), max(b[2] for b in boxes), max(b[3] for b in boxes))
        if boxes
        else None
    )
    frames = []
    for drawing in drawings:
        frame = drawing.crop(box) if box else drawing.copy()
        frame.thumbnail((FRAME_SIZE, FRAME_SIZE), Image.Resampling.LANCZOS)
        # The art is white line work: only its transparency carries the drawing.
        white = Image.new("L", frame.size, 255)
        frames.append(Image.merge("RGBA", (white, white, white, frame.getchannel("A"))))
    return frames


def main() -> None:
    drawings = sorted(set(json.loads(ART_MAP.read_text(encoding="utf-8")).values()))
    FRAMES_OUTPUT.mkdir(parents=True, exist_ok=True)
    expected: set[Path] = set()
    for drawing_id in drawings:
        sources = [download(drawing_id, frame) for frame in FRAMES]

        thumb = OUTPUT / f"{drawing_id}.webp"
        thumbnail(sources[FRAMES.index(THUMBNAIL_FRAME)]).save(thumb, "WEBP", quality=80, method=6)
        expected.add(thumb)

        for frame_number, frame in zip(FRAMES, movement_frames(sources), strict=True):
            path = FRAMES_OUTPUT / f"{drawing_id}-{frame_number}.webp"
            # Line art compresses far better once its alpha channel is lossy too; 40 shows no artefacts.
            frame.save(path, "WEBP", quality=80, alpha_quality=40, method=6)
            expected.add(path)

    stale = [path for path in OUTPUT.rglob("*.webp") if path not in expected]
    for path in stale:
        path.unlink()
    print(f"{len(drawings)} drawings: {len(expected)} files in {OUTPUT.relative_to(FRONTEND)}, {len(stale)} stale removed")


if __name__ == "__main__":
    main()
