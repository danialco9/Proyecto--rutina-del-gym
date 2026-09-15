import { PlusIcon, Trash2Icon } from 'lucide-react'
import type { Dispatch } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardAction, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { formatKg } from '@/lib/format'
import type { DraftAction, DraftExercise } from './draft'
import { LastSessionHint } from './LastSessionHint'
import { SetRow } from './SetRow'

function formatTarget(entry: DraftExercise): string | null {
  if (entry.targetSets === null && entry.targetReps === null) {
    return null
  }
  const scheme = `${entry.targetSets ?? '–'} × ${entry.targetReps ?? '–'}`
  return entry.targetWeightKg === null ? scheme : `${scheme} · ${formatKg(entry.targetWeightKg)}`
}

interface ExerciseCardProps {
  entry: DraftExercise
  dispatch: Dispatch<DraftAction>
  onSetCompleted: () => void
}

export function ExerciseCard({ entry, dispatch, onSetCompleted }: ExerciseCardProps) {
  const target = formatTarget(entry)

  return (
    <Card size="sm">
      <CardHeader>
        <CardTitle>{entry.name}</CardTitle>
        <CardDescription className="space-y-0.5">
          {target && <span className="block">Objetivo: {target}</span>}
          <LastSessionHint exerciseId={entry.exerciseId} />
        </CardDescription>
        <CardAction>
          <Button
            variant="ghost"
            size="icon-sm"
            aria-label={`Quitar ${entry.name}`}
            onClick={() => dispatch({ type: 'removeExercise', entryId: entry.id })}
          >
            <Trash2Icon />
          </Button>
        </CardAction>
      </CardHeader>
      <CardContent className="space-y-2">
        {entry.sets.map((set, index) => (
          <SetRow
            key={set.id}
            number={index + 1}
            set={set}
            onAdjust={(field, delta) =>
              dispatch({ type: 'adjustSet', entryId: entry.id, setId: set.id, field, delta })
            }
            onChange={(changes) => dispatch({ type: 'updateSet', entryId: entry.id, setId: set.id, changes })}
            onToggleDone={() => {
              if (!set.done) {
                onSetCompleted()
              }
              dispatch({ type: 'toggleDone', entryId: entry.id, setId: set.id })
            }}
            onRemove={() => dispatch({ type: 'removeSet', entryId: entry.id, setId: set.id })}
          />
        ))}
        <Button
          variant="secondary"
          className="h-10 w-full"
          onClick={() => dispatch({ type: 'addSet', entryId: entry.id })}
        >
          <PlusIcon />
          Añadir serie
        </Button>
      </CardContent>
    </Card>
  )
}
