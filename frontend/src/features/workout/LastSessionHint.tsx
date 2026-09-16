import { HistoryIcon } from 'lucide-react'
import { formatKg, formatShortDate } from '@/lib/format'
import { useLastSession } from './queries'

export function LastSessionHint({ exerciseId }: { exerciseId: number }) {
  const lastSession = useLastSession(exerciseId)

  if (lastSession.status !== 'success') {
    return null
  }
  if (lastSession.data === null) {
    return <span className="block">Primera vez con este ejercicio</span>
  }
  const sets = lastSession.data.sets.filter((set) => !set.is_warmup)
  return (
    <span className="block">
      <HistoryIcon className="mr-1 inline size-3.5 align-[-2px]" aria-hidden />
      Última vez ({formatShortDate(lastSession.data.started_at)}):{' '}
      {sets.map((set) => `${formatKg(set.weight_kg)} × ${set.reps}`).join(' · ')}
    </span>
  )
}
