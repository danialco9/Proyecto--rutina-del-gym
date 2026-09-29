import type { Exercise } from '@/lib/types'
import artBySlug from './exercise-art.json'

const drawings: Readonly<Record<string, string>> = artBySlug

/**
 * The drawing for a catalog exercise, from workout-guide (CC BY-SA 4.0, see docs/credits.md).
 * Custom exercises have none, even if their slug happens to match a catalog one.
 */
export function exerciseThumbnailUrl(exercise: Pick<Exercise, 'slug' | 'is_custom'>): string | null {
  const drawing = drawingFor(exercise)
  return drawing ? `/exercise-art/${drawing}.webp` : null
}

/** The three frames of the movement (start, middle, end), all cropped alike so they can be animated. */
export function exerciseFrameUrls(exercise: Pick<Exercise, 'slug' | 'is_custom'>): string[] {
  const drawing = drawingFor(exercise)
  return drawing ? [1, 2, 3].map((frame) => `/exercise-art/frames/${drawing}-${frame}.webp`) : []
}

function drawingFor(exercise: Pick<Exercise, 'slug' | 'is_custom'>): string | undefined {
  return exercise.is_custom ? undefined : drawings[exercise.slug]
}
