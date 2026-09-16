import { ArrowDownIcon, ArrowUpIcon, Trash2Icon } from 'lucide-react'
import { useId } from 'react'
import type { FieldErrors, UseFormRegister } from 'react-hook-form'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { parseOptionalNumber, type RoutineExerciseValues, type RoutineFormValues } from './routine-form'

const TARGET_FIELDS = [
  { key: 'targetSets', label: 'Series', inputMode: 'numeric', placeholder: '4' },
  { key: 'targetReps', label: 'Reps', inputMode: 'numeric', placeholder: '10' },
  { key: 'targetWeightKg', label: 'Peso (kg)', inputMode: 'decimal', placeholder: '60' },
  { key: 'targetRpe', label: 'RPE', inputMode: 'decimal', placeholder: '8' },
] as const

interface RoutineExerciseFieldsProps {
  index: number
  name: string
  isFirst: boolean
  isLast: boolean
  register: UseFormRegister<RoutineFormValues>
  errors?: FieldErrors<RoutineExerciseValues>
  onMoveUp: () => void
  onMoveDown: () => void
  onRemove: () => void
}

export function RoutineExerciseFields({
  index,
  name,
  isFirst,
  isLast,
  register,
  errors,
  onMoveUp,
  onMoveDown,
  onRemove,
}: RoutineExerciseFieldsProps) {
  const baseId = useId()
  const messages = TARGET_FIELDS.map(({ key }) => errors?.[key]?.message).filter(Boolean)

  return (
    <div className="bg-card space-y-3 rounded-xl border p-3">
      <div className="flex items-start justify-between gap-2">
        <p className="pt-1 font-medium">
          <span className="text-muted-foreground mr-2 tabular-nums">{index + 1}.</span>
          {name}
        </p>
        <div className="flex shrink-0 gap-1">
          <Button
            type="button"
            variant="ghost"
            size="icon"
            aria-label={`Subir ${name}`}
            disabled={isFirst}
            onClick={onMoveUp}
          >
            <ArrowUpIcon />
          </Button>
          <Button
            type="button"
            variant="ghost"
            size="icon"
            aria-label={`Bajar ${name}`}
            disabled={isLast}
            onClick={onMoveDown}
          >
            <ArrowDownIcon />
          </Button>
          <Button type="button" variant="ghost" size="icon" aria-label={`Quitar ${name}`} onClick={onRemove}>
            <Trash2Icon />
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-4 gap-2">
        {TARGET_FIELDS.map(({ key, label, inputMode, placeholder }) => {
          const id = `${baseId}-${key}`
          return (
            <div key={key} className="space-y-1">
              <Label htmlFor={id} className="text-muted-foreground text-xs">
                {label}
              </Label>
              <Input
                id={id}
                inputMode={inputMode}
                placeholder={placeholder}
                className="h-10 px-1 text-center tabular-nums"
                aria-invalid={errors?.[key] ? true : undefined}
                {...register(`exercises.${index}.${key}`, { setValueAs: parseOptionalNumber })}
              />
            </div>
          )
        })}
      </div>

      {messages.length > 0 && <p className="text-destructive text-sm">{messages.join(' · ')}</p>}
    </div>
  )
}
