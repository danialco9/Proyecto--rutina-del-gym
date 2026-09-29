import { DumbbellIcon } from 'lucide-react'
import { cn } from 'cn'
import type { Exercise } from '@/lib/types'
import { exerciseThumbnailUrl } from './exercise-art'

interface ExerciseThumbnailProps {
  exercise: Pick<Exercise, 'slug' | 'is_custom'>
  className?: string
}

/** A round drawing of the exercise, or a dumbbell when there is none. Decorative: the name sits next to it. */
export function ExerciseThumbnail({ exercise, className }: ExerciseThumbnailProps) {
  const url = exerciseThumbnailUrl(exercise)
  return (
    <span
      aria-hidden="true"
      className={cn(
        'bg-muted flex size-12 shrink-0 items-center justify-center overflow-hidden rounded-full',
        className,
      )}
    >
      {url ? (
        <img src={url} alt="" width={48} height={48} loading="lazy" decoding="async" className="size-full" />
      ) : (
        <DumbbellIcon className="text-muted-foreground size-5" />
      )}
    </span>
  )
}
