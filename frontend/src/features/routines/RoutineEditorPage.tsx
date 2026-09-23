import { useParams } from 'react-router'
import { QueryStatus } from '@/components/QueryStatus'
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
  if (routines.isPending || routines.isError) {
    return <QueryStatus query={routines} loading="Cargando rutina…" error="No se pudo cargar la rutina." />
  }
  const routine = routines.data.find((item) => String(item.id) === routineId)
  if (routine === undefined) {
    return (
      <Alert variant="destructive">
        <AlertDescription>Esta rutina no existe o fue eliminada.</AlertDescription>
      </Alert>
    )
  }
  return <RoutineEditor key={routine.id} routine={routine} />
}
