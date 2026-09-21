import { CheckIcon, PencilIcon } from 'lucide-react'
import { formatDecimal, formatKg } from '@/lib/format'
import type { DraftSet } from './draft'

interface SummaryProps {
  number: number
  set: DraftSet
}

/** A set already logged: one tap reopens it for correcting. */
export function CompletedSetRow({ number, set, onEdit }: SummaryProps & { onEdit: () => void }) {
  return (
    <button
      type="button"
      onClick={onEdit}
      aria-label={`Corregir serie ${number}: ${formatKg(set.weightKg)} por ${set.reps} repeticiones`}
      className="hover:bg-muted flex w-full items-center gap-2 rounded-lg px-2 py-1.5 text-left text-sm transition-colors"
    >
      <CheckIcon className="text-primary size-4 shrink-0" aria-hidden />
      <span className="text-muted-foreground w-3 shrink-0 tabular-nums">{number}</span>
      <span className="min-w-0 flex-1 truncate tabular-nums">
        {formatKg(set.weightKg)} × {set.reps}
      </span>
      {set.rpe !== null && (
        <span className="text-muted-foreground shrink-0 text-xs tabular-nums">
          RPE {formatDecimal(set.rpe)}
        </span>
      )}
      <PencilIcon className="text-muted-foreground size-3.5 shrink-0" aria-hidden />
    </button>
  )
}

/** A set still to come, showing what the routine prefilled. */
export function PendingSetRow({ number, set }: SummaryProps) {
  return (
    <p className="text-muted-foreground flex items-center gap-2 px-2 py-1.5 text-sm">
      <span className="size-4 shrink-0" aria-hidden />
      <span className="w-3 shrink-0 tabular-nums">{number}</span>
      <span className="tabular-nums">
        {formatKg(set.weightKg)} × {set.reps}
      </span>
    </p>
  )
}
