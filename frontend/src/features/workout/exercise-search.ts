import { EQUIPMENT_LABELS, MUSCLE_GROUP_LABELS } from '@/lib/labels'
import type { Exercise } from '@/lib/types'

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
