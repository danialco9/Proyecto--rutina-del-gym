import { CloudUploadIcon, TriangleAlertIcon } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { formatDate, plural } from '@/lib/format'
import { removeQueuedWorkout } from './outbox'
import { useOutbox } from './useOutbox'

/**
 * Workouts finished without connection. They are not in the list below until the server has them,
 * so without this the home page would look as if the last session had been lost.
 */
export function PendingWorkouts() {
  const items = useOutbox()
  const waiting = items.filter((item) => !item.rejected).length
  const rejected = items.filter((item) => item.rejected)

  if (items.length === 0) {
    return null
  }

  return (
    <section aria-label="Entrenos sin subir" className="space-y-2">
      {waiting > 0 && (
        <p
          role="status"
          className="bg-card ring-foreground/10 flex items-center gap-3 rounded-xl p-4 text-sm ring-1"
        >
          <CloudUploadIcon className="text-primary size-5 shrink-0" aria-hidden />
          <span>
            <span className="block font-medium">
              {waiting} {plural(waiting, 'entreno pendiente de subir', 'entrenos pendientes de subir')}
            </span>
            <span className="text-muted-foreground block">
              {plural(
                waiting,
                'Está guardado en este móvil y se subirá solo',
                'Están guardados en este móvil y se subirán solos',
              )}{' '}
              cuando vuelva la conexión.
            </span>
          </span>
        </p>
      )}
      {rejected.map((item) => (
        <div
          key={item.payload.client_id}
          className="bg-card ring-destructive/40 flex items-center gap-3 rounded-xl p-4 text-sm ring-1"
        >
          <TriangleAlertIcon className="text-destructive size-5 shrink-0" aria-hidden />
          <span className="min-w-0 flex-1">
            <span className="block font-medium">Entreno del {formatDate(item.payload.started_at)}</span>
            <span className="text-muted-foreground block">
              El servidor no lo aceptó (quizá borraste su rutina o un ejercicio).
            </span>
          </span>
          <Button
            variant="outline"
            size="sm"
            onClick={() => {
              if (window.confirm('¿Descartar este entreno? No se podrá recuperar.')) {
                removeQueuedWorkout(item.payload.client_id)
              }
            }}
          >
            Descartar
          </Button>
        </div>
      ))}
    </section>
  )
}
