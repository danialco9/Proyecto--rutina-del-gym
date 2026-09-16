import { useParams } from 'react-router'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { useRoutines } from '@/features/workout/queries'
import { RoutineEditor } from './RoutineEditor'

/** Creates a routine at /rutinas/nueva and edits one at /rutinas/:routineId. */
export function RoutineEditorPage() {
  const { routineId } = useParams()
  const routines = useRoutines()

  if (routineId === undefined) {
    return <RoutineEditor key="new" />
  }
  if (routines.isPending) {
    return <p className="text-muted-foreground text-sm">Cargando rutina…</p>
  }
  const routine = routines.data?.find((item) => String(item.id) === routineId)
  if (routines.isError || routine === undefined) {
    return (
      <Alert variant="destructive">
        <AlertDescription>
          {routines.isError ? 'No se pudo cargar la rutina.' : 'Esta rutina no existe o fue eliminada.'}
        </AlertDescription>
      </Alert>
    )
  }
  return <RoutineEditor key={routine.id} routine={routine} />
}
