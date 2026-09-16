import { ChartLineIcon, ChevronRightIcon, DumbbellIcon } from 'lucide-react'
import { useState } from 'react'
import { Link } from 'react-router'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { buttonVariants } from '@/components/ui/button'
import { Card, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { useProgressOverview } from '@/features/progress/queries'
import { loadDraft } from '@/features/workout/draft'
import { useRecentWorkouts, useRoutines } from '@/features/workout/queries'
import { formatDate, formatDuration, plural } from '@/lib/format'
import type { Workout } from '@/lib/types'
import { cn } from '@/lib/utils'

function workoutSummary(workout: Workout): string {
  const exerciseCount = new Set(workout.sets.map((set) => set.exercise_id)).size
  const setCount = workout.sets.length
  return [
    formatDate(workout.started_at),
    formatDuration(workout.started_at, workout.ended_at),
    `${exerciseCount} ${plural(exerciseCount, 'ejercicio', 'ejercicios')}`,
    `${setCount} ${plural(setCount, 'serie', 'series')}`,
  ]
    .filter(Boolean)
    .join(' · ')
}

function ProgressSummary() {
  const overview = useProgressOverview()
  const recommendations = overview.data?.recommendations ?? []
  if (recommendations.length === 0) {
    return null
  }
  const count = (action: string) => recommendations.filter((item) => item.action === action).length
  const increases = count('increase_load')
  const deloads = count('deload')
  const summary = [
    `${increases} ${plural(increases, 'ejercicio listo', 'ejercicios listos')} para subir peso`,
    deloads > 0 && `${deloads} ${plural(deloads, 'descarga', 'descargas')}`,
  ]
    .filter(Boolean)
    .join(' · ')

  return (
    <Link
      to="/progreso"
      className="bg-card hover:bg-muted flex items-center justify-between gap-3 rounded-xl border p-4 transition-colors"
    >
      <span className="flex min-w-0 items-center gap-3">
        <ChartLineIcon className="text-primary size-5 shrink-0" aria-hidden />
        <span className="min-w-0">
          <span className="block font-medium">Próxima sesión</span>
          <span className="text-muted-foreground block text-sm">{summary}</span>
        </span>
      </span>
      <ChevronRightIcon className="text-muted-foreground size-5 shrink-0" aria-hidden />
    </Link>
  )
}

export function HomePage() {
  const [hasDraft] = useState(() => loadDraft() !== null)
  const workouts = useRecentWorkouts(5)
  const routines = useRoutines()
  const routineNames = new Map(routines.data?.map((routine) => [routine.id, routine.name]))

  return (
    <div className="space-y-8">
      <section className="space-y-4">
        <div className="space-y-1">
          <h1 className="font-heading text-2xl font-semibold">Tu entrenamiento, medido</h1>
          <p className="text-muted-foreground">Registra cada serie y decide con datos cuándo progresar.</p>
        </div>
        <Link to="/entrenar" className={cn(buttonVariants({ size: 'lg' }), 'h-12 w-full text-base')}>
          <DumbbellIcon />
          {hasDraft ? 'Continuar entreno' : 'Empezar entreno'}
        </Link>
        <ProgressSummary />
      </section>

      <section className="space-y-3">
        <h2 className="font-heading text-lg font-medium">Últimos entrenos</h2>
        {workouts.isPending && <p className="text-muted-foreground text-sm">Cargando…</p>}
        {workouts.isError && (
          <Alert variant="destructive">
            <AlertDescription>No se pudieron cargar tus entrenos.</AlertDescription>
          </Alert>
        )}
        {workouts.data?.length === 0 && (
          <p className="text-muted-foreground rounded-xl border border-dashed p-6 text-center text-sm">
            Todavía no has registrado ningún entreno.
          </p>
        )}
        <ul className="space-y-2">
          {workouts.data?.map((workout) => (
            <li key={workout.id}>
              <Card size="sm">
                <CardHeader>
                  <CardTitle>
                    {workout.routine_id === null
                      ? 'Entreno libre'
                      : (routineNames.get(workout.routine_id) ?? 'Rutina')}
                  </CardTitle>
                  <CardDescription>{workoutSummary(workout)}</CardDescription>
                </CardHeader>
              </Card>
            </li>
          ))}
        </ul>
      </section>
    </div>
  )
}
