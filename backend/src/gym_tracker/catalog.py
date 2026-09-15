"""Built-in exercise catalog (Spanish names, English slugs) and its idempotent seeding."""

from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from gym_tracker.enums import Equipment, MuscleGroup
from gym_tracker.models import Exercise


@dataclass(frozen=True)
class CatalogExercise:
    slug: str
    name: str
    muscle_group: MuscleGroup
    equipment: Equipment
    secondary_muscles: tuple[MuscleGroup, ...] = ()


def _entry(
    slug: str, name: str, muscle_group: MuscleGroup, equipment: Equipment, *secondary: MuscleGroup
) -> CatalogExercise:
    return CatalogExercise(slug, name, muscle_group, equipment, secondary)


CATALOG: tuple[CatalogExercise, ...] = (
    # Chest
    _entry(
        "bench-press",
        "Press banca con barra",
        MuscleGroup.CHEST,
        Equipment.BARBELL,
        MuscleGroup.TRICEPS,
        MuscleGroup.SHOULDERS,
    ),
    _entry(
        "incline-bench-press",
        "Press inclinado con barra",
        MuscleGroup.CHEST,
        Equipment.BARBELL,
        MuscleGroup.SHOULDERS,
        MuscleGroup.TRICEPS,
    ),
    _entry(
        "dumbbell-bench-press",
        "Press banca con mancuernas",
        MuscleGroup.CHEST,
        Equipment.DUMBBELL,
        MuscleGroup.TRICEPS,
        MuscleGroup.SHOULDERS,
    ),
    _entry(
        "incline-dumbbell-press",
        "Press inclinado con mancuernas",
        MuscleGroup.CHEST,
        Equipment.DUMBBELL,
        MuscleGroup.SHOULDERS,
        MuscleGroup.TRICEPS,
    ),
    _entry(
        "smith-incline-press",
        "Press inclinado en multipower",
        MuscleGroup.CHEST,
        Equipment.SMITH_MACHINE,
        MuscleGroup.SHOULDERS,
        MuscleGroup.TRICEPS,
    ),
    _entry(
        "machine-chest-press",
        "Press de pecho en máquina",
        MuscleGroup.CHEST,
        Equipment.MACHINE,
        MuscleGroup.TRICEPS,
        MuscleGroup.SHOULDERS,
    ),
    _entry("pec-deck", "Contractora (pec deck)", MuscleGroup.CHEST, Equipment.MACHINE, MuscleGroup.SHOULDERS),
    _entry("cable-crossover", "Cruce de poleas", MuscleGroup.CHEST, Equipment.CABLE, MuscleGroup.SHOULDERS),
    _entry("dumbbell-fly", "Aperturas con mancuernas", MuscleGroup.CHEST, Equipment.DUMBBELL, MuscleGroup.SHOULDERS),
    _entry("push-up", "Flexiones", MuscleGroup.CHEST, Equipment.BODYWEIGHT, MuscleGroup.TRICEPS, MuscleGroup.SHOULDERS),
    _entry(
        "chest-dip",
        "Fondos en paralelas",
        MuscleGroup.CHEST,
        Equipment.BODYWEIGHT,
        MuscleGroup.TRICEPS,
        MuscleGroup.SHOULDERS,
    ),
    # Back
    _entry("pull-up", "Dominadas", MuscleGroup.BACK, Equipment.BODYWEIGHT, MuscleGroup.BICEPS),
    _entry("lat-pulldown", "Jalón al pecho", MuscleGroup.BACK, Equipment.CABLE, MuscleGroup.BICEPS),
    _entry("close-grip-lat-pulldown", "Jalón agarre estrecho", MuscleGroup.BACK, Equipment.CABLE, MuscleGroup.BICEPS),
    _entry(
        "barbell-row", "Remo con barra", MuscleGroup.BACK, Equipment.BARBELL, MuscleGroup.BICEPS, MuscleGroup.LOWER_BACK
    ),
    _entry("dumbbell-row", "Remo con mancuerna", MuscleGroup.BACK, Equipment.DUMBBELL, MuscleGroup.BICEPS),
    _entry("seated-cable-row", "Remo en polea baja", MuscleGroup.BACK, Equipment.CABLE, MuscleGroup.BICEPS),
    _entry("machine-row", "Remo en máquina", MuscleGroup.BACK, Equipment.MACHINE, MuscleGroup.BICEPS),
    _entry("t-bar-row", "Remo en T", MuscleGroup.BACK, Equipment.MACHINE, MuscleGroup.BICEPS, MuscleGroup.LOWER_BACK),
    _entry("straight-arm-pulldown", "Pullover en polea", MuscleGroup.BACK, Equipment.CABLE),
    _entry(
        "deadlift",
        "Peso muerto",
        MuscleGroup.LOWER_BACK,
        Equipment.BARBELL,
        MuscleGroup.GLUTES,
        MuscleGroup.HAMSTRINGS,
        MuscleGroup.TRAPS,
    ),
    _entry(
        "back-extension",
        "Hiperextensiones lumbares",
        MuscleGroup.LOWER_BACK,
        Equipment.BODYWEIGHT,
        MuscleGroup.GLUTES,
        MuscleGroup.HAMSTRINGS,
    ),
    _entry("barbell-shrug", "Encogimientos con barra", MuscleGroup.TRAPS, Equipment.BARBELL),
    _entry("dumbbell-shrug", "Encogimientos con mancuernas", MuscleGroup.TRAPS, Equipment.DUMBBELL),
    # Shoulders
    _entry("overhead-press", "Press militar con barra", MuscleGroup.SHOULDERS, Equipment.BARBELL, MuscleGroup.TRICEPS),
    _entry(
        "dumbbell-shoulder-press",
        "Press de hombro con mancuernas",
        MuscleGroup.SHOULDERS,
        Equipment.DUMBBELL,
        MuscleGroup.TRICEPS,
    ),
    _entry(
        "machine-shoulder-press",
        "Press de hombro en máquina",
        MuscleGroup.SHOULDERS,
        Equipment.MACHINE,
        MuscleGroup.TRICEPS,
    ),
    _entry("lateral-raise", "Elevaciones laterales con mancuernas", MuscleGroup.SHOULDERS, Equipment.DUMBBELL),
    _entry("cable-lateral-raise", "Elevaciones laterales en polea", MuscleGroup.SHOULDERS, Equipment.CABLE),
    _entry("machine-lateral-raise", "Elevaciones laterales en máquina", MuscleGroup.SHOULDERS, Equipment.MACHINE),
    _entry("front-raise", "Elevaciones frontales", MuscleGroup.SHOULDERS, Equipment.DUMBBELL),
    _entry(
        "reverse-pec-deck",
        "Pájaros en máquina",
        MuscleGroup.SHOULDERS,
        Equipment.MACHINE,
        MuscleGroup.BACK,
        MuscleGroup.TRAPS,
    ),
    _entry("face-pull", "Face pull", MuscleGroup.SHOULDERS, Equipment.CABLE, MuscleGroup.TRAPS, MuscleGroup.BACK),
    _entry("upright-row", "Remo al mentón", MuscleGroup.SHOULDERS, Equipment.BARBELL, MuscleGroup.TRAPS),
    # Biceps
    _entry("barbell-curl", "Curl de bíceps con barra", MuscleGroup.BICEPS, Equipment.BARBELL, MuscleGroup.FOREARMS),
    _entry("ez-bar-curl", "Curl con barra Z", MuscleGroup.BICEPS, Equipment.EZ_BAR, MuscleGroup.FOREARMS),
    _entry(
        "dumbbell-curl", "Curl de bíceps con mancuernas", MuscleGroup.BICEPS, Equipment.DUMBBELL, MuscleGroup.FOREARMS
    ),
    _entry("hammer-curl", "Curl martillo", MuscleGroup.BICEPS, Equipment.DUMBBELL, MuscleGroup.FOREARMS),
    _entry("incline-dumbbell-curl", "Curl inclinado con mancuernas", MuscleGroup.BICEPS, Equipment.DUMBBELL),
    _entry("preacher-curl", "Curl predicador (banco Scott)", MuscleGroup.BICEPS, Equipment.EZ_BAR),
    _entry("cable-curl", "Curl en polea", MuscleGroup.BICEPS, Equipment.CABLE),
    _entry("machine-curl", "Curl de bíceps en máquina", MuscleGroup.BICEPS, Equipment.MACHINE),
    # Triceps
    _entry("triceps-pushdown", "Extensión de tríceps en polea", MuscleGroup.TRICEPS, Equipment.CABLE),
    _entry("rope-pushdown", "Extensión de tríceps con cuerda", MuscleGroup.TRICEPS, Equipment.CABLE),
    _entry("overhead-cable-extension", "Extensión de tríceps tras nuca en polea", MuscleGroup.TRICEPS, Equipment.CABLE),
    _entry("skull-crusher", "Press francés", MuscleGroup.TRICEPS, Equipment.EZ_BAR),
    _entry(
        "close-grip-bench-press",
        "Press banca agarre estrecho",
        MuscleGroup.TRICEPS,
        Equipment.BARBELL,
        MuscleGroup.CHEST,
        MuscleGroup.SHOULDERS,
    ),
    _entry(
        "bench-dip",
        "Fondos en banco",
        MuscleGroup.TRICEPS,
        Equipment.BODYWEIGHT,
        MuscleGroup.CHEST,
        MuscleGroup.SHOULDERS,
    ),
    _entry("dumbbell-kickback", "Patada de tríceps", MuscleGroup.TRICEPS, Equipment.DUMBBELL),
    # Forearms
    _entry("wrist-curl", "Curl de muñeca", MuscleGroup.FOREARMS, Equipment.DUMBBELL),
    # Quads
    _entry(
        "back-squat",
        "Sentadilla con barra",
        MuscleGroup.QUADS,
        Equipment.BARBELL,
        MuscleGroup.GLUTES,
        MuscleGroup.HAMSTRINGS,
        MuscleGroup.LOWER_BACK,
    ),
    _entry("front-squat", "Sentadilla frontal", MuscleGroup.QUADS, Equipment.BARBELL, MuscleGroup.GLUTES),
    _entry("smith-squat", "Sentadilla en multipower", MuscleGroup.QUADS, Equipment.SMITH_MACHINE, MuscleGroup.GLUTES),
    _entry("hack-squat", "Sentadilla hack", MuscleGroup.QUADS, Equipment.MACHINE, MuscleGroup.GLUTES),
    _entry(
        "leg-press",
        "Prensa de piernas",
        MuscleGroup.QUADS,
        Equipment.MACHINE,
        MuscleGroup.GLUTES,
        MuscleGroup.HAMSTRINGS,
    ),
    _entry("leg-extension", "Extensión de cuádriceps", MuscleGroup.QUADS, Equipment.MACHINE),
    _entry("bulgarian-split-squat", "Sentadilla búlgara", MuscleGroup.QUADS, Equipment.DUMBBELL, MuscleGroup.GLUTES),
    _entry(
        "walking-lunge", "Zancadas", MuscleGroup.QUADS, Equipment.DUMBBELL, MuscleGroup.GLUTES, MuscleGroup.HAMSTRINGS
    ),
    _entry("goblet-squat", "Sentadilla goblet", MuscleGroup.QUADS, Equipment.DUMBBELL, MuscleGroup.GLUTES),
    # Hamstrings and glutes
    _entry(
        "romanian-deadlift",
        "Peso muerto rumano",
        MuscleGroup.HAMSTRINGS,
        Equipment.BARBELL,
        MuscleGroup.GLUTES,
        MuscleGroup.LOWER_BACK,
    ),
    _entry("lying-leg-curl", "Curl femoral tumbado", MuscleGroup.HAMSTRINGS, Equipment.MACHINE),
    _entry("seated-leg-curl", "Curl femoral sentado", MuscleGroup.HAMSTRINGS, Equipment.MACHINE),
    _entry("hip-thrust", "Hip thrust con barra", MuscleGroup.GLUTES, Equipment.BARBELL, MuscleGroup.HAMSTRINGS),
    _entry("cable-glute-kickback", "Patada de glúteo en polea", MuscleGroup.GLUTES, Equipment.CABLE),
    _entry(
        "hip-abduction-machine", "Abductores en máquina", MuscleGroup.ABDUCTORS, Equipment.MACHINE, MuscleGroup.GLUTES
    ),
    _entry("hip-adduction-machine", "Aductores en máquina", MuscleGroup.ADDUCTORS, Equipment.MACHINE),
    # Calves
    _entry("standing-calf-raise", "Elevación de gemelos de pie", MuscleGroup.CALVES, Equipment.MACHINE),
    _entry("seated-calf-raise", "Elevación de gemelos sentado", MuscleGroup.CALVES, Equipment.MACHINE),
    _entry("leg-press-calf-raise", "Gemelos en prensa", MuscleGroup.CALVES, Equipment.MACHINE),
    # Abs
    _entry("crunch", "Crunch abdominal", MuscleGroup.ABS, Equipment.BODYWEIGHT),
    _entry("cable-crunch", "Crunch en polea", MuscleGroup.ABS, Equipment.CABLE),
    _entry("machine-crunch", "Crunch en máquina", MuscleGroup.ABS, Equipment.MACHINE),
    _entry("hanging-leg-raise", "Elevación de piernas colgado", MuscleGroup.ABS, Equipment.BODYWEIGHT),
    _entry("ab-wheel-rollout", "Rueda abdominal", MuscleGroup.ABS, Equipment.BODYWEIGHT),
)

_UPDATABLE_COLUMNS = ("name", "muscle_group", "secondary_muscles", "equipment")


def seed_catalog(session: Session) -> int:
    """Insert or update every catalog exercise; safe to run repeatedly. Returns the catalog size."""
    rows = [
        {
            "user_id": None,
            "slug": exercise.slug,
            "name": exercise.name,
            "muscle_group": exercise.muscle_group.value,
            "secondary_muscles": [muscle.value for muscle in exercise.secondary_muscles],
            "equipment": exercise.equipment.value,
        }
        for exercise in CATALOG
    ]
    statement = insert(Exercise).values(rows)
    statement = statement.on_conflict_do_update(
        constraint="uq_exercises_user_id_slug",
        set_={column: statement.excluded[column] for column in _UPDATABLE_COLUMNS},
    )
    session.execute(statement)
    return len(rows)
