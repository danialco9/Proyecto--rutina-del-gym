"""URL-friendly identifiers."""

import re
import unicodedata

MAX_SLUG_LENGTH = 100
SLUG_PATTERN = r"^[a-z0-9]+(?:-[a-z0-9]+)*$"


def slugify(value: str, fallback: str = "exercise") -> str:
    """Lowercase ASCII kebab-case: ``"Jalón al pecho"`` becomes ``"jalon-al-pecho"``."""
    ascii_text = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^a-z0-9]+", "-", ascii_text.lower()).strip("-")
    return slug[:MAX_SLUG_LENGTH].rstrip("-") or fallback
