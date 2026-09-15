import { CheckIcon, Trash2Icon } from 'lucide-react'
import { useId } from 'react'
import { Button } from '@/components/ui/button'
import { Label } from '@/components/ui/label'
import { formatDecimal } from '@/lib/format'
import { WEIGHT_STEP_KG, type DraftSet } from './draft'
import { Stepper } from './Stepper'

const RPE_OPTIONS = [6, 6.5, 7, 7.5, 8, 8.5, 9, 9.5, 10]

interface SetRowProps {
  number: number
  set: DraftSet
  onAdjust: (field: 'reps' | 'weightKg', delta: number) => void
  onChange: (changes: Partial<Pick<DraftSet, 'reps' | 'weightKg' | 'rpe'>>) => void
  onToggleDone: () => void
  onRemove: () => void
}

export function SetRow({ number, set, onAdjust, onChange, onToggleDone, onRemove }: SetRowProps) {
  const rpeId = useId()

  return (
    <div
      data-done={set.done}
      className="data-[done=true]:border-primary/50 data-[done=true]:bg-primary/5 rounded-lg border p-2 transition-colors"
    >
      <div className="flex items-center justify-between">
        <span className="text-sm font-medium">Serie {number}</span>
        <div className="flex items-center gap-1">
          <Button variant="ghost" size="icon-sm" aria-label={`Eliminar serie ${number}`} onClick={onRemove}>
            <Trash2Icon />
          </Button>
          <Button
            variant={set.done ? 'default' : 'outline'}
            size="icon-lg"
            className="size-10"
            aria-pressed={set.done}
            aria-label={set.done ? `Serie ${number} completada` : `Completar serie ${number}`}
            onClick={onToggleDone}
          >
            <CheckIcon />
          </Button>
        </div>
      </div>

      <div className="mt-2 grid grid-cols-2 gap-2">
        <Stepper
          label="Peso (kg)"
          value={set.weightKg}
          step={WEIGHT_STEP_KG}
          inputMode="decimal"
          onAdjust={(delta) => onAdjust('weightKg', delta)}
          onChange={(weightKg) => onChange({ weightKg })}
        />
        <Stepper
          label="Reps"
          value={set.reps}
          step={1}
          inputMode="numeric"
          onAdjust={(delta) => onAdjust('reps', delta)}
          onChange={(reps) => onChange({ reps })}
        />
      </div>

      <div className="mt-2 flex items-center gap-2">
        <Label htmlFor={rpeId} className="text-muted-foreground text-xs">
          Esfuerzo (RPE)
        </Label>
        <select
          id={rpeId}
          value={set.rpe ?? ''}
          onChange={(event) =>
            onChange({ rpe: event.target.value === '' ? null : Number(event.target.value) })
          }
          className="border-input dark:bg-input/30 h-9 flex-1 rounded-lg border bg-transparent px-2 text-sm"
        >
          <option value="">Sin indicar</option>
          {RPE_OPTIONS.map((rpe) => (
            <option key={rpe} value={rpe}>
              {formatDecimal(rpe)}
            </option>
          ))}
        </select>
      </div>
    </div>
  )
}
