import { CheckIcon, ChevronRightIcon } from 'lucide-react'
import { Link } from 'react-router'
import { cn } from '@/lib/utils'

interface Step {
  to: string
  title: string
  hint: string
  done: boolean
}

interface GettingStartedProps {
  hasRoutine: boolean
  hasWorkout: boolean
  hasWeight: boolean
}

/**
 * A new account opens on an empty home screen, with nothing saying where to begin. This checklist
 * reads the account's own data, ticks each step as it is done and goes away once there is a routine
 * and a saved workout; the weight is optional, so it never keeps the card alive on its own.
 */
export function GettingStarted({ hasRoutine, hasWorkout, hasWeight }: GettingStartedProps) {
  if (hasRoutine && hasWorkout) return null

  const steps: Step[] = [
    { to: '/rutinas/nueva', title: 'Crea tu rutina', hint: 'Ejercicios, series y peso', done: hasRoutine },
    { to: '/entrenar', title: 'Haz tu primer entreno', hint: 'Serie a serie, sin prisa', done: hasWorkout },
    { to: '/medidas', title: 'Apunta tu peso (opcional)', hint: 'Para ver tu evolución', done: hasWeight },
  ]

  return (
    <section aria-labelledby="getting-started" className="bg-card ring-foreground/10 rounded-xl p-2 ring-1">
      <h2 id="getting-started" className="eyebrow px-3 pt-2 pb-1">
        Primeros pasos
      </h2>
      <ol>
        {steps.map((step, index) => {
          const marker = (
            <span
              className={cn(
                'flex size-8 shrink-0 items-center justify-center rounded-full text-sm font-semibold',
                step.done ? 'bg-primary text-primary-foreground' : 'bg-primary/10 text-primary',
              )}
              aria-hidden
            >
              {step.done ? <CheckIcon className="size-4" /> : index + 1}
            </span>
          )
          const text = (
            <span className="min-w-0">
              <span className={cn('block font-medium', step.done && 'text-muted-foreground line-through')}>
                {step.title}
              </span>
              <span className="text-muted-foreground block text-sm">{step.hint}</span>
            </span>
          )
          return (
            <li key={step.to}>
              {step.done ? (
                <p className="flex items-center gap-3 p-3">
                  {marker}
                  {text}
                  <span className="sr-only">(hecho)</span>
                </p>
              ) : (
                <Link
                  to={step.to}
                  className="hover:bg-accent flex items-center justify-between gap-3 rounded-lg p-3 transition-colors"
                >
                  <span className="flex min-w-0 items-center gap-3">
                    {marker}
                    {text}
                  </span>
                  <ChevronRightIcon className="text-muted-foreground size-5 shrink-0" aria-hidden />
                </Link>
              )}
            </li>
          )
        })}
      </ol>
    </section>
  )
}
