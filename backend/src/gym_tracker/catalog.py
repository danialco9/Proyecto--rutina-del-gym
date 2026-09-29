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
    _entry(
        "decline-bench-press",
        "Press declinado con barra",
        MuscleGroup.CHEST,
        Equipment.BARBELL,
        MuscleGroup.TRICEPS,
        MuscleGroup.SHOULDERS,
    ),
    _entry(
        "decline-dumbbell-press",
        "Press declinado con mancuernas",
        MuscleGroup.CHEST,
        Equipment.DUMBBELL,
        MuscleGroup.TRICEPS,
        MuscleGroup.SHOULDERS,
    ),
    _entry(
        "smith-bench-press",
        "Press banca en multipower",
        MuscleGroup.CHEST,
        Equipment.SMITH_MACHINE,
        MuscleGroup.TRICEPS,
        MuscleGroup.SHOULDERS,
    ),
    _entry(
        "smith-decline-press",
        "Press declinado en multipower",
        MuscleGroup.CHEST,
        Equipment.SMITH_MACHINE,
        MuscleGroup.TRICEPS,
        MuscleGroup.SHOULDERS,
    ),
    _entry(
        "incline-machine-press",
        "Press inclinado en máquina",
        MuscleGroup.CHEST,
        Equipment.MACHINE,
        MuscleGroup.SHOULDERS,
        MuscleGroup.TRICEPS,
    ),
    _entry(
        "decline-machine-press",
        "Press declinado en máquina",
        MuscleGroup.CHEST,
        Equipment.MACHINE,
        MuscleGroup.TRICEPS,
        MuscleGroup.SHOULDERS,
    ),
    _entry(
        "cable-chest-press",
        "Press de pecho en polea",
        MuscleGroup.CHEST,
        Equipment.CABLE,
        MuscleGroup.TRICEPS,
        MuscleGroup.SHOULDERS,
    ),
    _entry(
        "dumbbell-floor-press",
        "Press en el suelo con mancuernas",
        MuscleGroup.CHEST,
        Equipment.DUMBBELL,
        MuscleGroup.TRICEPS,
        MuscleGroup.SHOULDERS,
    ),
    _entry(
        "incline-dumbbell-fly",
        "Aperturas inclinadas con mancuernas",
        MuscleGroup.CHEST,
        Equipment.DUMBBELL,
        MuscleGroup.SHOULDERS,
    ),
    _entry(
        "decline-dumbbell-fly",
        "Aperturas declinadas con mancuernas",
        MuscleGroup.CHEST,
        Equipment.DUMBBELL,
        MuscleGroup.SHOULDERS,
    ),
    _entry(
        "flat-cable-fly", "Aperturas en polea en banco plano", MuscleGroup.CHEST, Equipment.CABLE, MuscleGroup.SHOULDERS
    ),
    _entry(
        "incline-cable-fly",
        "Aperturas en polea en banco inclinado",
        MuscleGroup.CHEST,
        Equipment.CABLE,
        MuscleGroup.SHOULDERS,
    ),
    _entry(
        "dumbbell-pullover",
        "Pullover con mancuerna",
        MuscleGroup.CHEST,
        Equipment.DUMBBELL,
        MuscleGroup.BACK,
        MuscleGroup.TRICEPS,
    ),
    _entry(
        "incline-push-up",
        "Flexiones inclinadas",
        MuscleGroup.CHEST,
        Equipment.BODYWEIGHT,
        MuscleGroup.TRICEPS,
        MuscleGroup.SHOULDERS,
    ),
    _entry(
        "decline-push-up",
        "Flexiones con pies elevados",
        MuscleGroup.CHEST,
        Equipment.BODYWEIGHT,
        MuscleGroup.TRICEPS,
        MuscleGroup.SHOULDERS,
    ),
    _entry(
        "wide-push-up",
        "Flexiones abiertas",
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
    _entry("wide-grip-lat-pulldown", "Jalón agarre ancho", MuscleGroup.BACK, Equipment.CABLE, MuscleGroup.BICEPS),
    _entry(
        "neutral-grip-lat-pulldown",
        "Jalón agarre neutro (triángulo)",
        MuscleGroup.BACK,
        Equipment.CABLE,
        MuscleGroup.BICEPS,
    ),
    _entry("reverse-grip-lat-pulldown", "Jalón agarre supino", MuscleGroup.BACK, Equipment.CABLE, MuscleGroup.BICEPS),
    _entry(
        "single-arm-lat-pulldown", "Jalón unilateral en polea", MuscleGroup.BACK, Equipment.CABLE, MuscleGroup.BICEPS
    ),
    _entry("chin-up", "Dominadas supinas", MuscleGroup.BACK, Equipment.BODYWEIGHT, MuscleGroup.BICEPS),
    _entry(
        "neutral-grip-pull-up", "Dominadas agarre neutro", MuscleGroup.BACK, Equipment.BODYWEIGHT, MuscleGroup.BICEPS
    ),
    _entry(
        "band-assisted-pull-up", "Dominadas asistidas con banda", MuscleGroup.BACK, Equipment.BAND, MuscleGroup.BICEPS
    ),
    _entry(
        "assisted-pull-up-machine",
        "Dominadas asistidas en máquina",
        MuscleGroup.BACK,
        Equipment.MACHINE,
        MuscleGroup.BICEPS,
    ),
    _entry(
        "pendlay-row", "Remo Pendlay", MuscleGroup.BACK, Equipment.BARBELL, MuscleGroup.BICEPS, MuscleGroup.LOWER_BACK
    ),
    _entry(
        "reverse-grip-barbell-row",
        "Remo con barra agarre supino",
        MuscleGroup.BACK,
        Equipment.BARBELL,
        MuscleGroup.BICEPS,
        MuscleGroup.LOWER_BACK,
    ),
    _entry("smith-row", "Remo en multipower", MuscleGroup.BACK, Equipment.SMITH_MACHINE, MuscleGroup.BICEPS),
    _entry(
        "chest-supported-dumbbell-row",
        "Remo con mancuernas en banco inclinado",
        MuscleGroup.BACK,
        Equipment.DUMBBELL,
        MuscleGroup.BICEPS,
    ),
    _entry(
        "chest-supported-t-bar-row",
        "Remo en T con apoyo de pecho",
        MuscleGroup.BACK,
        Equipment.MACHINE,
        MuscleGroup.BICEPS,
    ),
    _entry("meadows-row", "Remo Meadows (landmine)", MuscleGroup.BACK, Equipment.BARBELL, MuscleGroup.BICEPS),
    _entry("single-arm-cable-row", "Remo unilateral en polea", MuscleGroup.BACK, Equipment.CABLE, MuscleGroup.BICEPS),
    _entry("high-row-machine", "Remo alto en máquina", MuscleGroup.BACK, Equipment.MACHINE, MuscleGroup.BICEPS),
    _entry("iso-row-machine", "Remo unilateral en máquina", MuscleGroup.BACK, Equipment.MACHINE, MuscleGroup.BICEPS),
    _entry("inverted-row", "Remo invertido", MuscleGroup.BACK, Equipment.BODYWEIGHT, MuscleGroup.BICEPS),
    _entry("rope-straight-arm-pulldown", "Pullover en polea con cuerda", MuscleGroup.BACK, Equipment.CABLE),
    _entry(
        "barbell-pullover",
        "Pullover con barra",
        MuscleGroup.BACK,
        Equipment.BARBELL,
        MuscleGroup.CHEST,
        MuscleGroup.TRICEPS,
    ),
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
    _entry(
        "sumo-deadlift",
        "Peso muerto sumo",
        MuscleGroup.LOWER_BACK,
        Equipment.BARBELL,
        MuscleGroup.GLUTES,
        MuscleGroup.QUADS,
        MuscleGroup.HAMSTRINGS,
        MuscleGroup.ADDUCTORS,
    ),
    _entry(
        "trap-bar-deadlift",
        "Peso muerto con barra hexagonal",
        MuscleGroup.LOWER_BACK,
        Equipment.BARBELL,
        MuscleGroup.QUADS,
        MuscleGroup.GLUTES,
        MuscleGroup.HAMSTRINGS,
        MuscleGroup.TRAPS,
    ),
    _entry(
        "rack-pull",
        "Rack pull (peso muerto desde soportes)",
        MuscleGroup.LOWER_BACK,
        Equipment.BARBELL,
        MuscleGroup.GLUTES,
        MuscleGroup.HAMSTRINGS,
        MuscleGroup.TRAPS,
    ),
    _entry("barbell-shrug", "Encogimientos con barra", MuscleGroup.TRAPS, Equipment.BARBELL),
    _entry("dumbbell-shrug", "Encogimientos con mancuernas", MuscleGroup.TRAPS, Equipment.DUMBBELL),
    _entry("smith-shrug", "Encogimientos en multipower", MuscleGroup.TRAPS, Equipment.SMITH_MACHINE),
    _entry("cable-shrug", "Encogimientos en polea", MuscleGroup.TRAPS, Equipment.CABLE),
    _entry("machine-shrug", "Encogimientos en máquina", MuscleGroup.TRAPS, Equipment.MACHINE),
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
    _entry("arnold-press", "Press Arnold", MuscleGroup.SHOULDERS, Equipment.DUMBBELL, MuscleGroup.TRICEPS),
    _entry(
        "smith-shoulder-press",
        "Press de hombro en multipower",
        MuscleGroup.SHOULDERS,
        Equipment.SMITH_MACHINE,
        MuscleGroup.TRICEPS,
    ),
    _entry(
        "push-press", "Push press", MuscleGroup.SHOULDERS, Equipment.BARBELL, MuscleGroup.TRICEPS, MuscleGroup.QUADS
    ),
    _entry(
        "kettlebell-press",
        "Press de hombro con kettlebell",
        MuscleGroup.SHOULDERS,
        Equipment.KETTLEBELL,
        MuscleGroup.TRICEPS,
    ),
    _entry(
        "rear-delt-fly",
        "Pájaros con mancuernas",
        MuscleGroup.SHOULDERS,
        Equipment.DUMBBELL,
        MuscleGroup.BACK,
        MuscleGroup.TRAPS,
    ),
    _entry(
        "cable-rear-delt-fly",
        "Pájaros en polea",
        MuscleGroup.SHOULDERS,
        Equipment.CABLE,
        MuscleGroup.BACK,
        MuscleGroup.TRAPS,
    ),
    _entry("cable-front-raise", "Elevaciones frontales en polea", MuscleGroup.SHOULDERS, Equipment.CABLE),
    _entry("plate-front-raise", "Elevaciones frontales con disco", MuscleGroup.SHOULDERS, Equipment.BARBELL),
    _entry(
        "dumbbell-upright-row",
        "Remo al mentón con mancuernas",
        MuscleGroup.SHOULDERS,
        Equipment.DUMBBELL,
        MuscleGroup.TRAPS,
    ),
    _entry("cable-upright-row", "Remo al mentón en polea", MuscleGroup.SHOULDERS, Equipment.CABLE, MuscleGroup.TRAPS),
    _entry(
        "band-pull-apart",
        "Aperturas con banda",
        MuscleGroup.SHOULDERS,
        Equipment.BAND,
        MuscleGroup.BACK,
        MuscleGroup.TRAPS,
    ),
    _entry("cable-external-rotation", "Rotación externa en polea", MuscleGroup.SHOULDERS, Equipment.CABLE),
    _entry(
        "barbell-rear-delt-row",
        "Remo para deltoide posterior con barra",
        MuscleGroup.SHOULDERS,
        Equipment.BARBELL,
        MuscleGroup.BACK,
        MuscleGroup.TRAPS,
    ),
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
    _entry("concentration-curl", "Curl concentrado", MuscleGroup.BICEPS, Equipment.DUMBBELL),
    _entry("spider-curl", "Curl araña", MuscleGroup.BICEPS, Equipment.EZ_BAR),
    _entry("bayesian-cable-curl", "Curl bayesiano en polea", MuscleGroup.BICEPS, Equipment.CABLE),
    _entry("high-cable-curl", "Curl en polea alta", MuscleGroup.BICEPS, Equipment.CABLE),
    _entry(
        "rope-hammer-curl",
        "Curl martillo en polea con cuerda",
        MuscleGroup.BICEPS,
        Equipment.CABLE,
        MuscleGroup.FOREARMS,
    ),
    _entry(
        "cross-body-hammer-curl", "Curl martillo cruzado", MuscleGroup.BICEPS, Equipment.DUMBBELL, MuscleGroup.FOREARMS
    ),
    _entry(
        "incline-hammer-curl", "Curl martillo inclinado", MuscleGroup.BICEPS, Equipment.DUMBBELL, MuscleGroup.FOREARMS
    ),
    _entry("dumbbell-preacher-curl", "Curl predicador con mancuerna", MuscleGroup.BICEPS, Equipment.DUMBBELL),
    _entry("cable-preacher-curl", "Curl predicador en polea", MuscleGroup.BICEPS, Equipment.CABLE),
    _entry("drag-curl", "Drag curl con barra", MuscleGroup.BICEPS, Equipment.BARBELL),
    _entry("zottman-curl", "Curl Zottman", MuscleGroup.BICEPS, Equipment.DUMBBELL, MuscleGroup.FOREARMS),
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
    _entry(
        "overhead-dumbbell-extension",
        "Extensión de tríceps tras nuca con mancuerna",
        MuscleGroup.TRICEPS,
        Equipment.DUMBBELL,
    ),
    _entry("dumbbell-skull-crusher", "Press francés con mancuernas", MuscleGroup.TRICEPS, Equipment.DUMBBELL),
    _entry("single-arm-pushdown", "Extensión de tríceps unilateral en polea", MuscleGroup.TRICEPS, Equipment.CABLE),
    _entry("reverse-grip-pushdown", "Extensión de tríceps agarre supino", MuscleGroup.TRICEPS, Equipment.CABLE),
    _entry("v-bar-pushdown", "Extensión de tríceps con barra en V", MuscleGroup.TRICEPS, Equipment.CABLE),
    _entry("cable-kickback", "Patada de tríceps en polea", MuscleGroup.TRICEPS, Equipment.CABLE),
    _entry("machine-triceps-extension", "Extensión de tríceps en máquina", MuscleGroup.TRICEPS, Equipment.MACHINE),
    _entry(
        "machine-dip",
        "Fondos en máquina",
        MuscleGroup.TRICEPS,
        Equipment.MACHINE,
        MuscleGroup.CHEST,
        MuscleGroup.SHOULDERS,
    ),
    _entry(
        "triceps-dip",
        "Fondos en paralelas para tríceps",
        MuscleGroup.TRICEPS,
        Equipment.BODYWEIGHT,
        MuscleGroup.CHEST,
        MuscleGroup.SHOULDERS,
    ),
    _entry("jm-press", "Press JM", MuscleGroup.TRICEPS, Equipment.BARBELL, MuscleGroup.CHEST),
    _entry(
        "smith-close-grip-bench-press",
        "Press agarre estrecho en multipower",
        MuscleGroup.TRICEPS,
        Equipment.SMITH_MACHINE,
        MuscleGroup.CHEST,
        MuscleGroup.SHOULDERS,
    ),
    _entry(
        "diamond-push-up",
        "Flexiones diamante",
        MuscleGroup.TRICEPS,
        Equipment.BODYWEIGHT,
        MuscleGroup.CHEST,
        MuscleGroup.SHOULDERS,
    ),
    # Forearms
    _entry("wrist-curl", "Curl de muñeca", MuscleGroup.FOREARMS, Equipment.DUMBBELL),
    _entry("reverse-wrist-curl", "Curl de muñeca inverso", MuscleGroup.FOREARMS, Equipment.BARBELL),
    _entry("barbell-wrist-curl", "Curl de muñeca con barra", MuscleGroup.FOREARMS, Equipment.BARBELL),
    _entry(
        "reverse-barbell-curl", "Curl inverso con barra", MuscleGroup.FOREARMS, Equipment.BARBELL, MuscleGroup.BICEPS
    ),
    _entry("cable-wrist-curl", "Curl de muñeca en polea", MuscleGroup.FOREARMS, Equipment.CABLE),
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
    _entry("pendulum-squat", "Sentadilla péndulo", MuscleGroup.QUADS, Equipment.MACHINE, MuscleGroup.GLUTES),
    _entry(
        "belt-squat", "Sentadilla con cinturón (belt squat)", MuscleGroup.QUADS, Equipment.MACHINE, MuscleGroup.GLUTES
    ),
    _entry(
        "box-squat",
        "Sentadilla al cajón",
        MuscleGroup.QUADS,
        Equipment.BARBELL,
        MuscleGroup.GLUTES,
        MuscleGroup.HAMSTRINGS,
    ),
    _entry("dumbbell-squat", "Sentadilla con mancuernas", MuscleGroup.QUADS, Equipment.DUMBBELL, MuscleGroup.GLUTES),
    _entry("bodyweight-squat", "Sentadilla sin peso", MuscleGroup.QUADS, Equipment.BODYWEIGHT, MuscleGroup.GLUTES),
    _entry(
        "kettlebell-goblet-squat",
        "Sentadilla goblet con kettlebell",
        MuscleGroup.QUADS,
        Equipment.KETTLEBELL,
        MuscleGroup.GLUTES,
    ),
    _entry(
        "sumo-squat",
        "Sentadilla sumo con mancuerna",
        MuscleGroup.QUADS,
        Equipment.DUMBBELL,
        MuscleGroup.ADDUCTORS,
        MuscleGroup.GLUTES,
    ),
    _entry("barbell-hack-squat", "Sentadilla hack con barra", MuscleGroup.QUADS, Equipment.BARBELL, MuscleGroup.GLUTES),
    _entry(
        "single-leg-press",
        "Prensa a una pierna",
        MuscleGroup.QUADS,
        Equipment.MACHINE,
        MuscleGroup.GLUTES,
        MuscleGroup.HAMSTRINGS,
    ),
    _entry(
        "smith-leg-press",
        "Prensa en multipower",
        MuscleGroup.QUADS,
        Equipment.SMITH_MACHINE,
        MuscleGroup.GLUTES,
        MuscleGroup.HAMSTRINGS,
    ),
    _entry("single-leg-extension", "Extensión de cuádriceps a una pierna", MuscleGroup.QUADS, Equipment.MACHINE),
    _entry("sissy-squat", "Sissy squat", MuscleGroup.QUADS, Equipment.BODYWEIGHT),
    _entry(
        "barbell-lunge",
        "Zancadas con barra",
        MuscleGroup.QUADS,
        Equipment.BARBELL,
        MuscleGroup.GLUTES,
        MuscleGroup.HAMSTRINGS,
    ),
    _entry(
        "reverse-lunge",
        "Zancada hacia atrás",
        MuscleGroup.QUADS,
        Equipment.DUMBBELL,
        MuscleGroup.GLUTES,
        MuscleGroup.HAMSTRINGS,
    ),
    _entry(
        "static-lunge", "Zancada estática con mancuernas", MuscleGroup.QUADS, Equipment.DUMBBELL, MuscleGroup.GLUTES
    ),
    _entry(
        "smith-split-squat", "Zancada en multipower", MuscleGroup.QUADS, Equipment.SMITH_MACHINE, MuscleGroup.GLUTES
    ),
    _entry("bodyweight-lunge", "Zancadas sin peso", MuscleGroup.QUADS, Equipment.BODYWEIGHT, MuscleGroup.GLUTES),
    _entry("step-up", "Subidas al cajón con mancuernas", MuscleGroup.QUADS, Equipment.DUMBBELL, MuscleGroup.GLUTES),
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
    _entry(
        "dumbbell-romanian-deadlift",
        "Peso muerto rumano con mancuernas",
        MuscleGroup.HAMSTRINGS,
        Equipment.DUMBBELL,
        MuscleGroup.GLUTES,
        MuscleGroup.LOWER_BACK,
    ),
    _entry(
        "stiff-leg-deadlift",
        "Peso muerto piernas rígidas",
        MuscleGroup.HAMSTRINGS,
        Equipment.BARBELL,
        MuscleGroup.GLUTES,
        MuscleGroup.LOWER_BACK,
    ),
    _entry(
        "smith-romanian-deadlift",
        "Peso muerto rumano en multipower",
        MuscleGroup.HAMSTRINGS,
        Equipment.SMITH_MACHINE,
        MuscleGroup.GLUTES,
        MuscleGroup.LOWER_BACK,
    ),
    _entry(
        "single-leg-romanian-deadlift",
        "Peso muerto rumano a una pierna",
        MuscleGroup.HAMSTRINGS,
        Equipment.DUMBBELL,
        MuscleGroup.GLUTES,
    ),
    _entry(
        "good-morning",
        "Buenos días con barra",
        MuscleGroup.HAMSTRINGS,
        Equipment.BARBELL,
        MuscleGroup.LOWER_BACK,
        MuscleGroup.GLUTES,
    ),
    _entry("standing-leg-curl", "Curl femoral de pie", MuscleGroup.HAMSTRINGS, Equipment.MACHINE),
    _entry("nordic-curl", "Curl nórdico", MuscleGroup.HAMSTRINGS, Equipment.BODYWEIGHT),
    _entry("glute-ham-raise", "Glute ham raise (GHD)", MuscleGroup.HAMSTRINGS, Equipment.MACHINE, MuscleGroup.GLUTES),
    _entry(
        "hip-thrust-machine", "Hip thrust en máquina", MuscleGroup.GLUTES, Equipment.MACHINE, MuscleGroup.HAMSTRINGS
    ),
    _entry(
        "smith-hip-thrust",
        "Hip thrust en multipower",
        MuscleGroup.GLUTES,
        Equipment.SMITH_MACHINE,
        MuscleGroup.HAMSTRINGS,
    ),
    _entry(
        "barbell-glute-bridge",
        "Puente de glúteo con barra",
        MuscleGroup.GLUTES,
        Equipment.BARBELL,
        MuscleGroup.HAMSTRINGS,
    ),
    _entry(
        "single-leg-glute-bridge",
        "Puente de glúteo a una pierna",
        MuscleGroup.GLUTES,
        Equipment.BODYWEIGHT,
        MuscleGroup.HAMSTRINGS,
    ),
    _entry(
        "glute-kickback-machine",
        "Patada de glúteo en máquina",
        MuscleGroup.GLUTES,
        Equipment.MACHINE,
        MuscleGroup.HAMSTRINGS,
    ),
    _entry("cable-pull-through", "Pull-through en polea", MuscleGroup.GLUTES, Equipment.CABLE, MuscleGroup.HAMSTRINGS),
    _entry(
        "kettlebell-swing",
        "Swing con kettlebell",
        MuscleGroup.GLUTES,
        Equipment.KETTLEBELL,
        MuscleGroup.HAMSTRINGS,
        MuscleGroup.LOWER_BACK,
    ),
    _entry(
        "cable-hip-abduction",
        "Abducción de cadera en polea",
        MuscleGroup.ABDUCTORS,
        Equipment.CABLE,
        MuscleGroup.GLUTES,
    ),
    _entry("band-lateral-walk", "Paseo lateral con banda", MuscleGroup.ABDUCTORS, Equipment.BAND, MuscleGroup.GLUTES),
    _entry("cable-hip-adduction", "Aducción de cadera en polea", MuscleGroup.ADDUCTORS, Equipment.CABLE),
    # Calves
    _entry("standing-calf-raise", "Elevación de gemelos de pie", MuscleGroup.CALVES, Equipment.MACHINE),
    _entry("seated-calf-raise", "Elevación de gemelos sentado", MuscleGroup.CALVES, Equipment.MACHINE),
    _entry("leg-press-calf-raise", "Gemelos en prensa", MuscleGroup.CALVES, Equipment.MACHINE),
    _entry("smith-calf-raise", "Elevación de gemelos en multipower", MuscleGroup.CALVES, Equipment.SMITH_MACHINE),
    _entry(
        "single-leg-calf-raise",
        "Elevación de gemelos a una pierna con mancuerna",
        MuscleGroup.CALVES,
        Equipment.DUMBBELL,
    ),
    _entry("donkey-calf-raise", "Elevación de gemelos tipo burro", MuscleGroup.CALVES, Equipment.MACHINE),
    # Abs
    _entry("crunch", "Crunch abdominal", MuscleGroup.ABS, Equipment.BODYWEIGHT),
    _entry("cable-crunch", "Crunch en polea", MuscleGroup.ABS, Equipment.CABLE),
    _entry("machine-crunch", "Crunch en máquina", MuscleGroup.ABS, Equipment.MACHINE),
    _entry("hanging-leg-raise", "Elevación de piernas colgado", MuscleGroup.ABS, Equipment.BODYWEIGHT),
    _entry("ab-wheel-rollout", "Rueda abdominal", MuscleGroup.ABS, Equipment.BODYWEIGHT),
    _entry("reverse-crunch", "Crunch inverso", MuscleGroup.ABS, Equipment.BODYWEIGHT),
    _entry("decline-crunch", "Crunch declinado", MuscleGroup.ABS, Equipment.BODYWEIGHT),
    _entry("oblique-crunch", "Crunch oblicuo", MuscleGroup.ABS, Equipment.BODYWEIGHT),
    _entry("bicycle-crunch", "Crunch bicicleta", MuscleGroup.ABS, Equipment.BODYWEIGHT),
    _entry("sit-up", "Abdominales completos (sit-up)", MuscleGroup.ABS, Equipment.BODYWEIGHT),
    _entry("v-up", "Abdominales en V (navaja)", MuscleGroup.ABS, Equipment.BODYWEIGHT),
    _entry("captains-chair-knee-raise", "Elevación de rodillas en paralelas", MuscleGroup.ABS, Equipment.BODYWEIGHT),
    _entry("lying-leg-raise", "Elevación de piernas tumbado", MuscleGroup.ABS, Equipment.BODYWEIGHT),
    _entry("russian-twist", "Giro ruso", MuscleGroup.ABS, Equipment.BODYWEIGHT),
    _entry("cable-woodchopper", "Leñador en polea", MuscleGroup.ABS, Equipment.CABLE),
    _entry("pallof-press", "Press Pallof", MuscleGroup.ABS, Equipment.CABLE),
    _entry("dumbbell-side-bend", "Inclinación lateral con mancuerna", MuscleGroup.ABS, Equipment.DUMBBELL),
    _entry("dead-bug", "Dead bug", MuscleGroup.ABS, Equipment.BODYWEIGHT),
    _entry("barbell-rollout", "Rueda abdominal con barra", MuscleGroup.ABS, Equipment.BARBELL),
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
