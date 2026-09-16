# Training log data

Interim training log kept as CSV files until the web app is ready. The columns
mirror the planned PostgreSQL schema so the data can be imported with no changes.

| File | Description |
| --- | --- |
| `exercises.csv` | Exercise catalog (`exercise_id` is a slug, e.g. `leg-press`) |
| `routines.csv` | Routine templates (e.g. `push`, `pull`, `legs`) |
| `routine_exercises.csv` | One row per planned set of each exercise in a routine (`set_number`, optional target reps, weight and RPE) |
| `workouts.csv` | One row per training session |
| `workout_sets.csv` | One row per set performed |
| `body_measurements.csv` | Body weight and measurements over time |

## Conventions

- Dates use ISO 8601 (`YYYY-MM-DD`).
- Weights are in kilograms, lengths in centimeters.
- `rpe` is Rate of Perceived Exertion (1-10); `10` means no reps left in reserve.
- `is_warmup` is `true` or `false`.
- `workout_id` format: `YYYY-MM-DD-<n>` (e.g. `2026-09-15-1`).
- Lists inside a cell (e.g. `secondary_muscles`) are separated by `|`.
