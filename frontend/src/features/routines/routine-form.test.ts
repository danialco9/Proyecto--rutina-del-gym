import { describe, expect, it } from 'vitest'
import type { Routine } from '@/lib/types'
import { formToRoutinePayload, parseOptionalNumber, routineFormSchema, routineToForm } from './routine-form'

const legDay: Routine = {
  id: 7,
  name: 'Pierna',
  description: null,
  created_at: '2026-09-15T10:00:00Z',
  exercises: [
    {
      id: 1,
      position: 1,
      target_sets: 4,
      target_reps: 8,
      target_weight_kg: 60,
      target_rpe: null,
      exercise: {
        id: 11,
        slug: 'back-squat',
        name: 'Sentadilla con barra',
        muscle_group: 'quads',
        secondary_muscles: [],
        equipment: 'barbell',
        is_custom: false,
      },
    },
  ],
}

describe('routine form', () => {
  it('loads an existing routine and converts it back to the API payload', () => {
    const values = routineToForm(legDay)

    expect(values).toEqual({
      name: 'Pierna',
      description: '',
      exercises: [
        {
          exerciseId: 11,
          name: 'Sentadilla con barra',
          targetSets: 4,
          targetReps: 8,
          targetWeightKg: 60,
          targetRpe: null,
        },
      ],
    })
    expect(formToRoutinePayload({ ...values, name: '  Pierna A ', description: '   ' })).toEqual({
      name: 'Pierna A',
      description: null,
      exercises: [
        { exercise_id: 11, target_sets: 4, target_reps: 8, target_weight_kg: 60, target_rpe: null },
      ],
    })
  })

  it('parses optional numeric inputs', () => {
    expect(parseOptionalNumber('')).toBeNull()
    expect(parseOptionalNumber(' 8 ')).toBe(8)
    expect(parseOptionalNumber('52,5')).toBe(52.5)
    expect(parseOptionalNumber('abc')).toBeNaN()
  })

  it('validates the name and the targets with Spanish messages', () => {
    const result = routineFormSchema.safeParse({
      name: '  ',
      description: '',
      exercises: [
        {
          exerciseId: 11,
          name: 'Sentadilla',
          targetSets: 0,
          targetReps: 1.5,
          targetWeightKg: Number.NaN,
          targetRpe: 11,
        },
      ],
    })

    expect(result.success).toBe(false)
    expect(result.error?.issues.map((issue) => issue.message)).toEqual(
      expect.arrayContaining([
        'Ponle un nombre a la rutina',
        'Series: mínimo 1',
        'Reps: usa un número entero',
        'Peso: introduce un número',
        'RPE: máximo 10',
      ]),
    )
  })
})
