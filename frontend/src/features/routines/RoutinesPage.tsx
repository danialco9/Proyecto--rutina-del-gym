import { ChevronRightIcon, PlusIcon } from 'lucide-react'
import { Link } from 'react-router'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { buttonVariants } from '@/components/ui/button'
import { useRoutines } from '@/features/workout/queries'
import { plural } from '@/lib/format'
import type { Routine } from '@/lib/types'
import { cn } from '@/lib/utils'

const PREVIEW_EXERCISES = 3

function routineSummary(routine: Routine): string {
  const count = routine.exercises.length
  if (count === 0) {
    return 'Sin ejercicios'
  }
  const names = routine.exercises.slice(0, PREVIEW_EXERCISES).map((item) => item.exercise.name)
  const more = count > PREVIEW_EXERCISES ? '…' : ''
  return `${count} ${plural(count, 'ejercicio', 'ejercicios')} · ${names.join(', ')}${more}`
}

export function RoutinesPage() {
  const routines = useRoutines()

  return (
    <div className="space-y-6">
      <header className="flex items-start justify-between gap-3">
        <div className="space-y-1">
          <h1 className="font-heading text-2xl font-semibold">Rutinas</h1>
          <p className="text-muted-foreground text-sm">
            Plantillas para empezar cada entreno con todo preparado.
          </p>
        </div>
        <Link to="/rutinas/nueva" className={cn(buttonVariants(), 'h-10 shrink-0')}>
          <PlusIcon />
          Nueva rutina
        </Link>
      </header>

      {routines.isPending && <p className="text-muted-foreground text-sm">Cargando rutinas…</p>}
      {routines.isError && (
        <Alert variant="destructive">
          <AlertDescription>No se pudieron cargar las rutinas.</AlertDescription>
        </Alert>
      )}
      {routines.data?.length === 0 && (
        <p className="text-muted-foreground rounded-xl border border-dashed p-6 text-center text-sm">
          Aún no tienes rutinas. Crea una con los ejercicios que sueles hacer cada día.
        </p>
      )}

      <ul className="space-y-2">
        {routines.data?.map((routine) => (
          <li key={routine.id}>
            <Link
              to={`/rutinas/${routine.id}`}
              className="bg-card hover:bg-muted flex items-center justify-between gap-3 rounded-xl border p-4 transition-colors"
            >
              <span className="min-w-0">
                <span className="block font-medium">{routine.name}</span>
                <span className="text-muted-foreground block truncate text-sm">
                  {routineSummary(routine)}
                </span>
              </span>
              <ChevronRightIcon className="text-muted-foreground size-5 shrink-0" aria-hidden />
            </Link>
          </li>
        ))}
      </ul>
    </div>
  )
}
