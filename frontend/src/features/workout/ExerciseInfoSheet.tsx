import { useEffect, useState } from 'react'
import { DumbbellIcon } from 'lucide-react'
import { cn } from 'cn'
import { Button } from '@/components/ui/button'
import { Sheet, SheetContent, SheetDescription, SheetTitle } from '@/components/ui/sheet'
import { EQUIPMENT_LABELS, MUSCLE_GROUP_LABELS } from '@/lib/labels'
import type { Exercise } from '@/lib/types'
import { exerciseFrameUrls } from './exercise-art'

interface ExerciseInfoSheetProps {
  /** The exercise to show; null keeps the sheet closed. */
  exercise: Exercise | null
  onClose: () => void
  onAdd: (exercise: Exercise) => void
}

export function ExerciseInfoSheet({ exercise, onClose, onAdd }: ExerciseInfoSheetProps) {
  return (
    <Sheet open={exercise !== null} onOpenChange={(open) => !open && onClose()}>
      <SheetContent
        side="bottom"
        className="mx-auto max-h-[90dvh] max-w-2xl gap-0 overflow-y-auto rounded-t-xl"
      >
        {exercise && <ExerciseInfo exercise={exercise} onAdd={onAdd} />}
      </SheetContent>
    </Sheet>
  )
}

function ExerciseInfo({ exercise, onAdd }: { exercise: Exercise; onAdd: (exercise: Exercise) => void }) {
  const frames = exerciseFrameUrls(exercise)
  const secondary = exercise.secondary_muscles.map((muscle) => MUSCLE_GROUP_LABELS[muscle]).join(', ')

  return (
    <div className="space-y-5 p-4 pt-12 pb-[max(1rem,env(safe-area-inset-bottom))]">
      {frames.length > 0 ? (
        <MovementAnimation frames={frames} />
      ) : (
        <div className="bg-muted mx-auto flex aspect-square w-full max-w-64 items-center justify-center rounded-2xl">
          <DumbbellIcon className="text-muted-foreground size-12" aria-hidden="true" />
        </div>
      )}

      <div className="space-y-1">
        <SheetTitle className="text-xl font-semibold">{exercise.name}</SheetTitle>
        <SheetDescription>
          {frames.length > 0
            ? 'El dibujo muestra el movimiento completo.'
            : 'Este ejercicio no tiene dibujo.'}
        </SheetDescription>
      </div>

      <dl className="grid grid-cols-[auto_1fr] gap-x-4 gap-y-2 text-sm">
        <dt className="text-muted-foreground">Músculo principal</dt>
        <dd className="font-medium">{MUSCLE_GROUP_LABELS[exercise.muscle_group]}</dd>
        {secondary && (
          <>
            <dt className="text-muted-foreground">Secundarios</dt>
            <dd>{secondary}</dd>
          </>
        )}
        {exercise.equipment && (
          <>
            <dt className="text-muted-foreground">Material</dt>
            <dd>{EQUIPMENT_LABELS[exercise.equipment]}</dd>
          </>
        )}
      </dl>

      <Button size="lg" className="h-12 w-full text-base" onClick={() => onAdd(exercise)}>
        Añadir
      </Button>
    </div>
  )
}

const FRAME_MS = 650
// Start, middle, end, middle: the movement goes there and back instead of jumping to the start.
const SEQUENCE = [0, 1, 2, 1]

function prefersReducedMotion(): boolean {
  return window.matchMedia?.('(prefers-reduced-motion: reduce)').matches ?? false
}

/** Cycles through the frames. All of them are mounted at once, so the loop never waits on a download. */
function MovementAnimation({ frames }: { frames: string[] }) {
  const [step, setStep] = useState(0)
  const [animate] = useState(() => !prefersReducedMotion())

  useEffect(() => {
    if (!animate) {
      return
    }
    const timer = window.setInterval(() => setStep((current) => (current + 1) % SEQUENCE.length), FRAME_MS)
    return () => window.clearInterval(timer)
  }, [animate])

  // With reduced motion the middle frame stays put: it is the most recognisable one.
  const visible = animate ? SEQUENCE[step] : 1

  return (
    <div
      role="img"
      aria-label="Dibujo del movimiento"
      className="bg-muted relative mx-auto aspect-square w-full max-w-64 overflow-hidden rounded-2xl"
    >
      {frames.map((src, index) => (
        <img
          key={src}
          src={src}
          alt=""
          className={cn('absolute inset-0 size-full object-contain p-4', index !== visible && 'opacity-0')}
        />
      ))}
    </div>
  )
}
