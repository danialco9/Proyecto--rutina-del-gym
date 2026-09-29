import { EQUIPMENT_LABELS, MUSCLE_GROUP_LABELS } from '@/lib/labels'
import type { Equipment, Exercise, MuscleGroup, Workout } from '@/lib/types'

export interface ExerciseFilters {
  muscle: MuscleGroup | null
  equipment: Equipment | null
}

/** Keeps exercises whose primary muscle and equipment match the chosen filters (null = any). */
export function applyFilters(exercises: Exercise[], filters: ExerciseFilters): Exercise[] {
  return exercises.filter(
    (exercise) =>
      (filters.muscle === null || exercise.muscle_group === filters.muscle) &&
      (filters.equipment === null || exercise.equipment === filters.equipment),
  )
}

/** The exercises trained most recently, newest first and without repeats. Expects workouts newest first. */
export function recentExercises(workouts: Workout[], exercises: Exercise[], limit = 6): Exercise[] {
  const byId = new Map(exercises.map((exercise) => [exercise.id, exercise]))
  const recent: Exercise[] = []
  const seen = new Set<number>()
  for (const workout of workouts) {
    for (const set of workout.sets) {
      const exercise = byId.get(set.exercise_id)
      if (exercise && !seen.has(exercise.id)) {
        seen.add(exercise.id)
        recent.push(exercise)
        if (recent.length === limit) {
          return recent
        }
      }
    }
  }
  return recent
}

export function normalizeText(value: string): string {
  return value
    .normalize('NFD')
    .replace(/\p{Diacritic}/gu, '')
    .toLowerCase()
    .trim()
}

/** Keeps exercises matching every search word in the name, muscle group or equipment, ignoring accents. */
export function filterExercises(exercises: Exercise[], query: string): Exercise[] {
  const words = normalizeText(query).split(/\s+/).filter(Boolean)
  if (words.length === 0) {
    return exercises
  }
  return exercises.filter((exercise) => {
    const searchable = normalizeText(
      [
        exercise.name,
        MUSCLE_GROUP_LABELS[exercise.muscle_group],
        exercise.equipment ? EQUIPMENT_LABELS[exercise.equipment] : '',
      ].join(' '),
    )
    return words.every((word) => searchable.includes(word))
  })
}
