import { MUSCLE_GROUP_LABELS } from '@/lib/labels'
import type { MuscleGroup, ProgressionAction, Recommendation, WeeklyVolume } from '@/lib/types'

export const ACTION_ORDER: readonly ProgressionAction[] = ['increase_load', 'increase_reps', 'hold', 'deload']

export const ACTION_TEXT: Record<ProgressionAction, { title: string; hint: string }> = {
  increase_load: { title: 'Sube el peso', hint: 'Completaste el objetivo con margen.' },
  increase_reps: { title: 'Busca más repeticiones', hint: 'Mantén el peso hasta completar el objetivo.' },
  hold: { title: 'Repite la sesión', hint: 'Completaste el objetivo, pero con mucho esfuerzo.' },
  deload: {
    title: 'Descarga',
    hint: 'Varias sesiones sin progresar: baja el peso y vuelve a construir.',
  },
}

export function groupRecommendations(recommendations: Recommendation[]) {
  return ACTION_ORDER.map((action) => ({
    action,
    items: recommendations
      .filter((item) => item.action === action)
      .toSorted((a, b) => a.exercise_name.localeCompare(b.exercise_name, 'es')),
  })).filter((group) => group.items.length > 0)
}

/** Stacked series beyond this many muscles fold into "Otros" (the palette has six validated slots). */
export const MAX_MUSCLE_SERIES = 6
export const OTHER_MUSCLES = 'other'
export type VolumeSeriesKey = MuscleGroup | typeof OTHER_MUSCLES

export const muscleLabel = (key: VolumeSeriesKey) =>
  key === OTHER_MUSCLES ? 'Otros' : MUSCLE_GROUP_LABELS[key]

export type VolumeRow = { week_start: string } & Partial<Record<VolumeSeriesKey, number>>

export interface MuscleWeekComparison {
  muscle: MuscleGroup
  currentWeek: number
  previousAverage: number
}

const AVERAGE_WEEKS = 4

/**
 * Prepares the weekly hard-set chart and table. Series are the muscles with the most sets over
 * the whole period, in that order, so each keeps its colour while the data stays the same.
 */
export function buildVolume(weeks: WeeklyVolume[]) {
  const totals = new Map<MuscleGroup, number>()
  for (const week of weeks) {
    for (const { muscle_group: muscle, hard_sets: sets } of week.muscles) {
      totals.set(muscle, (totals.get(muscle) ?? 0) + sets)
    }
  }
  const ranked = [...totals.entries()]
    .toSorted(([muscleA, a], [muscleB, b]) => b - a || muscleA.localeCompare(muscleB))
    .map(([muscle]) => muscle)
  const needsOther = ranked.length > MAX_MUSCLE_SERIES
  const shown = needsOther ? ranked.slice(0, MAX_MUSCLE_SERIES - 1) : ranked
  const series: VolumeSeriesKey[] = needsOther ? [...shown, OTHER_MUSCLES] : shown

  const rows: VolumeRow[] = weeks.map((week) => {
    const row: VolumeRow = { week_start: week.week_start }
    for (const { muscle_group: muscle, hard_sets: sets } of week.muscles) {
      const key: VolumeSeriesKey = shown.includes(muscle) ? muscle : OTHER_MUSCLES
      row[key] = (row[key] ?? 0) + sets
    }
    return row
  })

  const current = weeks.at(-1)
  const previous = weeks.slice(-1 - AVERAGE_WEEKS, -1)
  const setsIn = (week: WeeklyVolume | undefined, muscle: MuscleGroup) =>
    week?.muscles.find((item) => item.muscle_group === muscle)?.hard_sets ?? 0
  const comparison: MuscleWeekComparison[] = ranked
    .map((muscle) => ({
      muscle,
      currentWeek: setsIn(current, muscle),
      previousAverage:
        previous.length === 0
          ? 0
          : Math.round(
              (previous.reduce((sum, week) => sum + setsIn(week, muscle), 0) / previous.length) * 10,
            ) / 10,
    }))
    .filter((row) => row.currentWeek > 0 || row.previousAverage > 0)
    .toSorted((a, b) => b.currentWeek - a.currentWeek || b.previousAverage - a.previousAverage)

  return { series, rows, comparison }
}

/** CSS colour for the n-th categorical series, in the validated slot order. */
export const seriesColor = (index: number) => `var(--chart-${index + 1})`
