import { WifiOffIcon } from 'lucide-react'
import { useSyncExternalStore } from 'react'

function subscribe(onChange: () => void) {
  window.addEventListener('online', onChange)
  window.addEventListener('offline', onChange)
  return () => {
    window.removeEventListener('online', onChange)
    window.removeEventListener('offline', onChange)
  }
}

function useOnline() {
  return useSyncExternalStore(
    subscribe,
    () => window.navigator.onLine,
    () => true,
  )
}

/**
 * Installed on a phone, the app opens with no connection at all, so it has to say so: the workout
 * draft survives in `localStorage`, but saving it — and every other screen — needs the API.
 */
export function OfflineNotice() {
  const online = useOnline()
  if (online) return null

  return (
    <p
      role="status"
      className="bg-muted text-muted-foreground flex items-center justify-center gap-2 px-4 py-2 text-center text-xs"
    >
      <WifiOffIcon className="size-4 shrink-0" aria-hidden />
      Sin conexión. Lo que apuntes se queda en el móvil; podrás guardarlo cuando vuelva la cobertura.
    </p>
  )
}
