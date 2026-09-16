"""Command-line training report (Spanish output): ``uv run gym-report``."""

from __future__ import annotations

import argparse
import io
import sys
from pathlib import Path

import pandas as pd

from gym_tracker.analysis import (
    Action,
    PerformedSet,
    PlannedSet,
    Recommendation,
    TrainingLog,
    load_training_log,
    personal_records,
    recommend,
    weekly_volume_by_muscle,
    weekly_weight_change,
    weight_trend,
    working_sets,
)

DEFAULT_DATA_DIR = Path(__file__).resolve().parents[3] / "data"

ACTION_LABELS = {
    Action.INCREASE_LOAD: "Sube el peso",
    Action.INCREASE_REPS: "Mantén el peso y busca más repeticiones",
    Action.HOLD: "Repite la sesión (el esfuerzo fue alto)",
    Action.DELOAD: "Estancado: baja el peso y vuelve a construir",
}


def _format_kg(value: float) -> str:
    return f"{value:g} kg"


def _format_sets(sets: tuple[PlannedSet, ...] | tuple[PerformedSet, ...]) -> str:
    parts = []
    for item in sets:
        weight = "?" if item.weight_kg is None else f"{item.weight_kg:g}"
        parts.append(f"{weight}x{'?' if item.reps is None else item.reps}")
    return " · ".join(parts)


def _format_recommendation(item: Recommendation) -> str:
    target = f" (objetivo {_format_sets(item.target_sets)})" if item.target_sets else ""
    return (
        f"- {item.exercise_name}: último {_format_sets(item.last_sets)}{target} -> "
        f"{ACTION_LABELS[item.action]}: {_format_sets(item.suggested_sets)}"
    )


def _section(title: str) -> None:
    print(f"\n== {title} ==")


def build_report(log: TrainingLog) -> None:
    work = working_sets(log)
    names = log.exercises.set_index("exercise_id")["name"]

    _section("Récords personales")
    if work.empty:
        print("Aún no hay entrenos registrados.")
    else:
        for record in personal_records(work).to_dict(orient="records"):
            name = names.get(record["exercise_id"], record["exercise_id"])
            print(
                f"- {name}: e1RM {record['best_e1rm_kg']:.1f} kg ({record['best_e1rm_date']:%d/%m}), "
                f"peso máximo {_format_kg(record['max_weight_kg'])} ({record['max_weight_date']:%d/%m})"
            )

        _section("Series efectivas por músculo (últimas 4 semanas)")
        volume = weekly_volume_by_muscle(work, log.exercises)
        recent = volume[volume["week_start"] >= volume["week_start"].max() - pd.Timedelta(weeks=3)]
        table = recent.pivot_table(index="muscle_group", columns="week_start", values="hard_sets", fill_value=0)
        table = table.astype(int).rename_axis(index="músculo")
        table.columns = [f"{week:%d/%m}" for week in table.columns]
        print(table.to_string())

    _section("Peso corporal")
    trend = weight_trend(log.body_measurements)
    if trend.empty:
        print("Aún no hay medidas registradas.")
    else:
        latest = trend.iloc[-1]
        print(
            f"Último: {_format_kg(float(latest['weight_kg']))} ({latest['date']:%d/%m}), "
            f"media 7 días {latest['trend_kg']:.1f} kg"
        )
        change = weekly_weight_change(log.body_measurements)
        if change is not None:
            print(f"Tendencia: {change:+.2f} kg/semana (últimas 4 semanas)")

    _section("Recomendaciones para la próxima sesión")
    recommendations = recommend(log)
    if not recommendations:
        print("Registra al menos un entreno para recibir recomendaciones.")
    for item in recommendations:
        print(_format_recommendation(item))


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Informe de entrenamiento a partir del registro CSV.")
    parser.add_argument("--data-dir", type=Path, default=DEFAULT_DATA_DIR, help="Carpeta con los CSV del registro")
    args = parser.parse_args(argv)

    if isinstance(sys.stdout, io.TextIOWrapper):  # Windows consoles default to a legacy code page
        sys.stdout.reconfigure(encoding="utf-8")
    build_report(load_training_log(args.data_dir))


if __name__ == "__main__":
    main()
