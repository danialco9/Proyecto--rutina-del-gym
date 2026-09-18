import { ChevronRightIcon, PlusIcon } from 'lucide-react'
import { Link } from 'react-router'
import { PageHeader } from '@/components/PageHeader'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Button } from '@/components/ui/button'
import { plural } from '@/lib/format'
import type { Routine } from '@/lib/types'
import { useRoutines } from './queries'

interface StartWorkoutProps {
  onStart: (routine?: Routine) => void
}

export function StartWorkout({ onStart }: StartWorkoutProps) {
  const routines = useRoutines()

  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="Entrenar"
        title="Nuevo entreno"
        description="Elige una rutina o empieza un entreno libre."
      />

      <Button size="lg" className="h-12 w-full text-base sm:w-auto sm:px-8" onClick={() => onStart()}>
        <PlusIcon />
        Entreno libre
      </Button>

      <section className="space-y-3">
        <div className="flex items-center justify-between gap-2">
          <h2 className="eyebrow">Tus rutinas</h2>
          <Link to="/rutinas" className="text-primary text-sm font-medium underline-offset-4 hover:underline">
            Gestionar
          </Link>
        </div>
        {routines.isPending && <p className="text-muted-foreground text-sm">Cargando rutinas…</p>}
        {routines.isError && (
          <Alert variant="destructive">
            <AlertDescription>No se pudieron cargar las rutinas.</AlertDescription>
          </Alert>
        )}
        {routines.data?.length === 0 && (
          <p className="text-muted-foreground text-sm">
            Aún no tienes rutinas.{' '}
            <Link to="/rutinas/nueva" className="text-primary font-medium underline-offset-4 hover:underline">
              Crea tu primera rutina
            </Link>{' '}
            o empieza un entreno libre.
          </p>
        )}
        <ul className="grid gap-3 lg:grid-cols-2">
          {routines.data?.map((routine) => (
            <li key={routine.id}>
              <button
                type="button"
                onClick={() => onStart(routine)}
                className="bg-card ring-foreground/10 hover:bg-accent hover:ring-primary/40 flex h-full w-full items-center justify-between rounded-xl p-4 text-left ring-1 transition-colors"
              >
                <span>
                  <span className="block font-medium">{routine.name}</span>
                  <span className="text-muted-foreground text-sm">
                    {routine.exercises.length} {plural(routine.exercises.length, 'ejercicio', 'ejercicios')}
                  </span>
                </span>
                <ChevronRightIcon className="text-muted-foreground size-5" aria-hidden />
              </button>
            </li>
          ))}
        </ul>
      </section>
    </div>
  )
}
