import { TimerIcon } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { formatSeconds } from '@/lib/format'

interface RestTimerBarProps {
  remaining: number
  onAddTime: () => void
  onSkip: () => void
}

export function RestTimerBar({ remaining, onAddTime, onSkip }: RestTimerBarProps) {
  return (
    <div className="bg-background/95 fixed inset-x-0 bottom-[calc(3.5rem+env(safe-area-inset-bottom))] z-40 border-t backdrop-blur">
      <div className="mx-auto flex max-w-2xl items-center justify-between gap-2 px-4 py-2">
        <span role="timer" className="flex items-center gap-2 font-medium tabular-nums">
          <TimerIcon className="text-primary size-4" aria-hidden />
          Descanso {formatSeconds(remaining)}
        </span>
        <div className="flex gap-2">
          <Button variant="outline" size="sm" onClick={onAddTime}>
            +15 s
          </Button>
          <Button variant="ghost" size="sm" onClick={onSkip}>
            Saltar
          </Button>
        </div>
      </div>
    </div>
  )
}
