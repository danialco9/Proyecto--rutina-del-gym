import { describe, expect, it } from 'vitest'
import type { MuscleGroup, Recommendation, WeeklyVolume } from '@/lib/types'
import { buildVolume, groupRecommendations } from './progress-data'

function week(weekStart: string, sets: Partial<Record<MuscleGroup, number>>): WeeklyVolume {
  return {
    week_start: weekStart,
    muscles: Object.entries(sets).map(([muscle, hardSets]) => ({
      muscle_group: muscle as MuscleGroup,
      hard_sets: hardSets,
      volume_kg: hardSets * 500,
    })),
  }
}

function recommendation(name: string, action: Recommendation['action']): Recommendation {
  return {
    exercise_id: name.length,
    exercise_name: name,
    action,
    last_performed_on: '2026-09-15',
    last_weight_kg: 60,
    last_reps: [8, 8, 8],
    target_reps: 8,
    suggested_weight_kg: 62.5,
  }
}

describe('progress data', () => {
  it('groups recommendations by action in a fixed order', () => {
    const groups = groupRecommendations([
      recommendation('Sentadilla', 'deload'),
      recommendation('Press banca', 'increase_load'),
      recommendation('Jalón', 'increase_load'),
    ])

    expect(groups.map((group) => [group.action, group.items.map((item) => item.exercise_name)])).toEqual([
      ['increase_load', ['Jalón', 'Press banca']],
      ['deload', ['Sentadilla']],
    ])
  })

  it('keeps the busiest muscles as series and folds the rest into "other"', () => {
    const { series, rows } = buildVolume([
      week('2026-09-07', { chest: 9, back: 8, quads: 6, hamstrings: 4, shoulders: 3, biceps: 2, calves: 1 }),
      week('2026-09-14', { chest: 3, triceps: 2 }),
    ])

    expect(series).toEqual(['chest', 'back', 'quads', 'hamstrings', 'shoulders', 'other'])
    expect(rows).toEqual([
      { week_start: '2026-09-07', chest: 9, back: 8, quads: 6, hamstrings: 4, shoulders: 3, other: 3 },
      { week_start: '2026-09-14', chest: 3, other: 2 },
    ])
  })

  it('compares the current week with the average of the previous four', () => {
    const { comparison } = buildVolume([
      week('2026-08-10', { chest: 20 }),
      week('2026-08-17', { chest: 10, back: 6 }),
      week('2026-08-24', { chest: 10 }),
      week('2026-08-31', { chest: 12 }),
      week('2026-09-07', { chest: 9, back: 4 }),
      week('2026-09-14', { back: 5 }),
    ])

    expect(comparison).toEqual([
      { muscle: 'back', currentWeek: 5, previousAverage: 2.5 },
      { muscle: 'chest', currentWeek: 0, previousAverage: 10.3 },
    ])
  })

  it('has no series without training', () => {
    expect(buildVolume([week('2026-09-14', {})])).toEqual({
      series: [],
      rows: [{ week_start: '2026-09-14' }],
      comparison: [],
    })
  })
})
