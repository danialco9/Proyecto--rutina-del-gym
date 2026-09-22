import { MinusIcon, PlusIcon } from 'lucide-react'
import { useId, useState } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'

const toInputText = (value: number) => String(value).replace('.', ',')

interface StepperProps {
  label: string
  value: number
  step: number
  inputMode: 'decimal' | 'numeric'
  onAdjust: (delta: number) => void
  onChange: (value: number) => void
}

/** Number field with large -/+ buttons, comfortable to use between sets. */
export function Stepper({ label, value, step, inputMode, onAdjust, onChange }: StepperProps) {
  const id = useId()
  // Text being typed; null shows the committed value (e.g. after pressing -/+).
  const [text, setText] = useState<string | null>(null)
  const lowerLabel = label.toLowerCase()

  return (
    <div className="space-y-1">
      <Label htmlFor={id} className="text-muted-foreground text-xs">
        {label}
      </Label>
      <div className="flex items-center gap-1 sm:gap-1.5">
        <Button
          variant="outline"
          size="icon-lg"
          className="size-10 shrink-0 sm:size-11"
          aria-label={`Reducir ${lowerLabel}`}
          onClick={() => onAdjust(-step)}
        >
          <MinusIcon />
        </Button>
        <Input
          id={id}
          inputMode={inputMode}
          value={text ?? toInputText(value)}
          className="h-10 px-0.5 text-center text-base tabular-nums sm:h-11 sm:px-1"
          onFocus={(event) => {
            setText(toInputText(value))
            event.target.select()
          }}
          onChange={(event) => {
            setText(event.target.value)
            const parsed = Number(event.target.value.replace(',', '.'))
            if (event.target.value.trim() !== '' && Number.isFinite(parsed)) {
              onChange(parsed)
            }
          }}
          onBlur={() => setText(null)}
        />
        <Button
          variant="outline"
          size="icon-lg"
          className="size-10 shrink-0 sm:size-11"
          aria-label={`Aumentar ${lowerLabel}`}
          onClick={() => onAdjust(step)}
        >
          <PlusIcon />
        </Button>
      </div>
    </div>
  )
}
