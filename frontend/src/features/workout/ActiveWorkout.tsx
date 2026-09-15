import { PlusIcon } from 'lucide-react'
import { useState, type Dispatch } from 'react'
import { useNavigate } from 'react-router'
import { toast } from 'sonner'
import { Button } from '@/components/ui/button'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { formatTime, plural } from '@/lib/format'
import { completedSetCount, toWorkoutPayload, type DraftAction, type WorkoutDraft } from './draft'
import { ExerciseCard } from './ExerciseCard'
import { ExercisePicker } from './ExercisePicker'
import { useSaveWorkout } from './queries'
import { RestTimerBar } from './RestTimerBar'
import { useRestTimer } from './useRestTimer'

const EXTRA_REST_SECONDS = 15

interface ActiveWorkoutProps {
  draft: WorkoutDraft
  dispatch: Dispatch<DraftAction>
}

export function ActiveWorkout({ draft, dispatch }: ActiveWorkoutProps) {
  const [pickerOpen, setPickerOpen] = useState(false)
  const timer = useRestTimer()
  const saveWorkout = useSaveWorkout()
  const navigate = useNavigate()
  const completed = completedSetCount(draft)

  const finish = () => {
    saveWorkout.mutate(toWorkoutPayload(draft, new Date().toISOString()), {
      onSuccess: () => {
        timer.stop()
        dispatch({ type: 'discard' })
        toast.success('Entreno guardado')
        navigate('/')
      },
      onError: () => {
        toast.error('No se pudo guardar el entreno. El borrador sigue guardado en este dispositivo.')
      },
    })
  }

  const discard = () => {
    if (window.confirm('¿Descartar este entreno? Se perderán las series apuntadas.')) {
      timer.stop()
      dispatch({ type: 'discard' })
    }
  }

  return (
    <div className="space-y-4">
      <header className="flex items-start justify-between gap-2">
        <div className="space-y-1">
          <h1 className="font-heading text-xl font-semibold">{draft.routineName ?? 'Entreno libre'}</h1>
          <p className="text-muted-foreground text-sm">
            Empezado a las {formatTime(draft.startedAt)} · {completed} {plural(completed, 'serie', 'series')}{' '}
            {plural(completed, 'completada', 'completadas')}
          </p>
        </div>
        <Button variant="ghost" size="sm" onClick={discard}>
          Descartar
        </Button>
      </header>

      {draft.exercises.length === 0 && (
        <p className="text-muted-foreground rounded-xl border border-dashed p-6 text-center text-sm">
          Añade tu primer ejercicio para empezar.
        </p>
      )}

      {draft.exercises.map((entry) => (
        <ExerciseCard key={entry.id} entry={entry} dispatch={dispatch} onSetCompleted={() => timer.start()} />
      ))}

      <Button
        variant="outline"
        size="lg"
        className="h-12 w-full text-base"
        onClick={() => setPickerOpen(true)}
      >
        <PlusIcon />
        Añadir ejercicio
      </Button>

      <div className="space-y-2">
        <Label htmlFor="workout-notes">Notas</Label>
        <Textarea
          id="workout-notes"
          value={draft.notes}
          placeholder="Sensaciones, molestias, cambios…"
          onChange={(event) => dispatch({ type: 'setNotes', notes: event.target.value })}
        />
      </div>

      <Button
        size="lg"
        className="h-12 w-full text-base"
        disabled={completed === 0 || saveWorkout.isPending}
        onClick={finish}
      >
        {saveWorkout.isPending ? 'Guardando…' : 'Terminar y guardar'}
      </Button>

      <ExercisePicker
        open={pickerOpen}
        onOpenChange={setPickerOpen}
        onSelect={(exercise) => {
          dispatch({ type: 'addExercise', exercise })
          setPickerOpen(false)
        }}
      />

      {timer.isRunning && (
        <RestTimerBar
          remaining={timer.remaining}
          onAddTime={() => timer.addSeconds(EXTRA_REST_SECONDS)}
          onSkip={timer.stop}
        />
      )}
    </div>
  )
}
