import re

import pytest

from gym_tracker.catalog import CATALOG
from gym_tracker.slugs import SLUG_PATTERN, slugify


def test_catalog_slugs_and_names_are_unique() -> None:
    slugs = [exercise.slug for exercise in CATALOG]
    names = [exercise.name for exercise in CATALOG]

    assert len(set(slugs)) == len(slugs)
    assert len(set(names)) == len(names)


def test_catalog_slugs_are_kebab_case() -> None:
    assert [exercise.slug for exercise in CATALOG if not re.fullmatch(SLUG_PATTERN, exercise.slug)] == []


def test_catalog_primary_muscle_is_not_repeated_as_secondary() -> None:
    assert [exercise.slug for exercise in CATALOG if exercise.muscle_group in exercise.secondary_muscles] == []


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("Jalón al pecho", "jalon-al-pecho"),
        ("  Press   banca!! ", "press-banca"),
        ("Extensión de cuádriceps", "extension-de-cuadriceps"),
        ("¿?", "exercise"),
    ],
)
def test_slugify(value: str, expected: str) -> None:
    assert slugify(value) == expected
