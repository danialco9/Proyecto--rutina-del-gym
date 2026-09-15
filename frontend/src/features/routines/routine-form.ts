import { z } from 'zod'
import type { Routine, RoutineIn } from '@/lib/types'

function optionalTarget(label: string, min: number, max: number, integer = false) {
  const number = z.number({ error: `${label}: introduce un número` })
  const checked = integer ? number.int(`${label}: usa un número entero`) : number
  return checked.min(min, `${label}: mínimo ${min}`).max(max, `${label}: máximo ${max}`).nullable()
}

// Limits mirror the API validation (RoutineExerciseIn in backend/src/gym_tracker/schemas.py).
export const routineExerciseSchema = z.object({
  exerciseId: z.number().int(),
  name: z.string(),
  targetSets: optionalTarget('Series', 1, 20, true),
  targetReps: optionalTarget('Reps', 1, 100, true),
  targetWeightKg: optionalTarget('Peso', 0, 1000),
  targetRpe: optionalTarget('RPE', 1, 10),
})

export const routineFormSchema = z.object({
  name: z.string().trim().min(1, 'Ponle un nombre a la rutina').max(100, 'El nombre es demasiado largo'),
  description: z.string().max(2000, 'La descripción es demasiado larga'),
  exercises: z.array(routineExerciseSchema).max(30, 'Una rutina puede tener como máximo 30 ejercicios'),
})

export type RoutineExerciseValues = z.infer<typeof routineExerciseSchema>
export type RoutineFormValues = z.infer<typeof routineFormSchema>

export const emptyRoutineForm: RoutineFormValues = { name: '', description: '', exercises: [] }

export function routineToForm(routine: Routine): RoutineFormValues {
  return {
    name: routine.name,
    description: routine.description ?? '',
    exercises: routine.exercises.map((item) => ({
      exerciseId: item.exercise.id,
      name: item.exercise.name,
      targetSets: item.target_sets,
      targetReps: item.target_reps,
      targetWeightKg: item.target_weight_kg,
      targetRpe: item.target_rpe,
    })),
  }
}

export function formToRoutinePayload(values: RoutineFormValues): RoutineIn {
  return {
    name: values.name.trim(),
    description: values.description.trim() || null,
    exercises: values.exercises.map((item) => ({
      exercise_id: item.exerciseId,
      target_sets: item.targetSets,
      target_reps: item.targetReps,
      target_weight_kg: item.targetWeightKg,
      target_rpe: item.targetRpe,
    })),
  }
}

/** Reads an optional numeric input: empty means `null`, and a decimal comma is accepted. */
export function parseOptionalNumber(value: unknown): number | null {
  if (typeof value === 'number') {
    return value
  }
  const text = String(value ?? '')
    .trim()
    .replace(',', '.')
  return text === '' ? null : Number(text)
}
