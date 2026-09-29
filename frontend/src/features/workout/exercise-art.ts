import type { Exercise } from '@/lib/types'
import artBySlug from './exercise-art.json'

const drawings: Readonly<Record<string, string>> = artBySlug

/**
 * The drawing for a catalog exercise, from workout-guide (CC BY-SA 4.0, see docs/credits.md).
 * Custom exercises have none, even if their slug happens to match a catalog one.
 */
export function exerciseThumbnailUrl(exercise: Pick<Exercise, 'slug' | 'is_custom'>): string | null {
  const drawing = exercise.is_custom ? undefined : drawings[exercise.slug]
  return drawing ? `/exercise-art/${drawing}.webp` : null
}
