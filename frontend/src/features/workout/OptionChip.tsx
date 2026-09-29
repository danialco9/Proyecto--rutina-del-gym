import { cn } from 'cn'

interface OptionChipProps {
  label: string
  pressed: boolean
  onClick: () => void
}

/** A rounded toggle for picking one option out of a row of them. */
export function OptionChip({ label, pressed, onClick }: OptionChipProps) {
  return (
    <button
      type="button"
      aria-pressed={pressed}
      className={cn(
        'h-9 rounded-full border px-3.5 text-sm transition-colors',
        pressed ? 'border-primary bg-primary text-primary-foreground' : 'hover:bg-muted',
      )}
      onClick={onClick}
    >
      {label}
    </button>
  )
}
